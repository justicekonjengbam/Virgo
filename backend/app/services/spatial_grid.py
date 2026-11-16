from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, NamedTuple


@dataclass(frozen=True)
class SpatialRingTier:
    """Defines a concentric wave dispatch ring (Uber DISCO architecture)."""

    tier: int
    name: str
    max_hex: int
    max_km: float
    search_message: str


class DispatchCandidate(NamedTuple):
    """Dispatch candidate tuple maintaining backward-compatibility with (driver, distance_km)."""

    driver: Any
    distance_km: float
    cell_id: str
    tier: int
    hex_distance: int
    score: float
    tier_name: str


class HexSpatialGrid:
    """Hexagonal spatial grid index (Uber H3 equivalent) using axial and cube coordinates.

    Uses pointy-topped hexagonal tessellation with equal-area planar projection.
    Every hexagonal cell has 6 equidistant neighbors, preventing the corner distortion
    of square grids (S2/Geohash) and providing perfectly symmetric radial expansion.
    """

    def __init__(
        self,
        cell_radius_meters: float = 600.0,
        origin_lat: float = 24.8170,
        origin_lon: float = 93.9368,
    ) -> None:
        self.radius = cell_radius_meters
        self.origin_lat = origin_lat
        self.origin_lon = origin_lon
        self.earth_radius = 6371000.0  # WGS84 earth radius in meters

    def lat_lon_to_cartesian(self, lat: float, lon: float) -> tuple[float, float]:
        """Project geographic lat/lon to local metric cartesian coordinates."""
        rad_lat = math.radians(lat)
        rad_lat0 = math.radians(self.origin_lat)
        d_lon = math.radians(lon - self.origin_lon)
        d_lat = math.radians(lat - self.origin_lat)
        x = self.earth_radius * d_lon * math.cos((rad_lat + rad_lat0) / 2.0)
        y = self.earth_radius * d_lat
        return x, y

    def cartesian_to_cube(self, x: float, y: float) -> tuple[int, int, int]:
        """Convert cartesian metric coordinates to hex cube coordinates (x_c, y_c, z_c)."""
        # Pointy-topped hex orientation
        q = (math.sqrt(3) / 3.0 * x - 1.0 / 3.0 * y) / self.radius
        r = (2.0 / 3.0 * y) / self.radius
        x_c, z_c = q, r
        y_c = -x_c - z_c

        rx, ry, rz = round(x_c), round(y_c), round(z_c)
        x_diff = abs(rx - x_c)
        y_diff = abs(ry - y_c)
        z_diff = abs(rz - z_c)

        if x_diff > y_diff and x_diff > z_diff:
            rx = -ry - rz
        elif y_diff > z_diff:
            ry = -rx - rz
        else:
            rz = -rx - ry

        return int(rx), int(ry), int(rz)

    def get_cell(self, lat: float, lon: float) -> tuple[str, tuple[int, int, int]]:
        """Return human-readable cell ID and cube coordinates for lat/lon."""
        x, y = self.lat_lon_to_cartesian(lat, lon)
        cube = self.cartesian_to_cube(x, y)
        cell_id = f'hex:{cube[0]}:{cube[2]}'
        return cell_id, cube

    @staticmethod
    def hex_distance(cell_a: tuple[int, int, int], cell_b: tuple[int, int, int]) -> int:
        """Calculate the exact hexagonal ring distance (k-ring) between two cells."""
        return (
            abs(cell_a[0] - cell_b[0])
            + abs(cell_a[1] - cell_b[1])
            + abs(cell_a[2] - cell_b[2])
        ) // 2

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance in kilometers using the Haversine formula."""
        rad_lat1, rad_lon1, rad_lat2, rad_lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
        dlat = rad_lat2 - rad_lat1
        dlon = rad_lon2 - rad_lon1
        a = math.sin(dlat / 2.0) ** 2 + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(dlon / 2.0) ** 2
        return 6371.0 * 2.0 * math.asin(math.sqrt(a))

    @staticmethod
    def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate initial compass bearing from (lat1, lon1) towards (lat2, lon2) in degrees [0, 360)."""
        rad_lat1, rad_lon1, rad_lat2, rad_lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
        dlon = rad_lon2 - rad_lon1
        y = math.sin(dlon) * math.cos(rad_lat2)
        x = math.cos(rad_lat1) * math.sin(rad_lat2) - math.sin(rad_lat1) * math.cos(rad_lat2) * math.cos(dlon)
        bearing = math.degrees(math.atan2(y, x))
        return (bearing + 360.0) % 360.0


class UberStyleDispatchSelector:
    """Dispatches rides using spatial cell indexing, expanding concentric rings, and multi-factor ranking.

    Architecture mirrors Uber's DISCO (Dispatch Service):
    1. World is partitioned into discrete hexagonal cells (resolution ~600m radius).
    2. Candidate search begins in the closest concentric ring (Tier 0).
    3. If no driver accepts or none is available in Tier 0, the search smoothly expands to Tier 1, then Tier 2, etc.
    4. Within each active ring tier, candidate drivers are scored using a weighted multi-factor formula:
       - Distance / ETA (50%)
       - Heading alignment towards pickup (20%)
       - Driver idle time fairness / anti-starvation (15%)
       - Driver rating & reliability (15%)
    """

    DEFAULT_TIERS: list[SpatialRingTier] = [
        SpatialRingTier(
            tier=0,
            name='Hyper-Local',
            max_hex=2,
            max_km=1.8,
            search_message='Connecting you with the closest drivers near you...',
        ),
        SpatialRingTier(
            tier=1,
            name='Neighborhood',
            max_hex=5,
            max_km=4.5,
            search_message='Contacting nearby drivers in your neighborhood...',
        ),
        SpatialRingTier(
            tier=2,
            name='District',
            max_hex=10,
            max_km=9.0,
            search_message='Expanding search to drivers in your district...',
        ),
        SpatialRingTier(
            tier=3,
            name='Metropolitan',
            max_hex=20,
            max_km=18.0,
            search_message='Reaching out to drivers in the wider area...',
        ),
        SpatialRingTier(
            tier=4,
            name='Regional',
            max_hex=999,
            max_km=40.0,
            search_message='Checking for available drivers across the region...',
        ),
    ]

    def __init__(
        self,
        grid: HexSpatialGrid | None = None,
        tiers: list[SpatialRingTier] | None = None,
    ) -> None:
        self.grid = grid or HexSpatialGrid()
        self.tiers = tiers or self.DEFAULT_TIERS

    def select_best_candidate(
        self,
        pickup_lat: float,
        pickup_lon: float,
        candidates: list[dict[str, Any]],
        excluded_driver_ids: set[int],
    ) -> DispatchCandidate | None:
        """Selects the highest scoring driver from the closest non-exhausted ring tier."""
        _, pickup_cube = self.grid.get_cell(pickup_lat, pickup_lon)
        candidates_by_tier: dict[int, list[DispatchCandidate]] = {t.tier: [] for t in self.tiers}

        for item in candidates:
            driver = item['driver']
            driver_id = driver.id
            if driver_id in excluded_driver_ids:
                continue

            lat = float(item['latitude'])
            lon = float(item['longitude'])
            dist_km = self.grid.haversine_km(lat, lon, pickup_lat, pickup_lon)

            # Max regional boundary check (40.0 km)
            if dist_km > self.tiers[-1].max_km:
                continue

            cell_id, cube = self.grid.get_cell(lat, lon)
            hex_dist = self.grid.hex_distance(pickup_cube, cube)

            # Assign to concentric ring tier
            assigned_tier = self.tiers[-1]
            for t in self.tiers:
                if hex_dist <= t.max_hex and dist_km <= t.max_km:
                    assigned_tier = t
                    break

            # Multi-factor scoring
            # 1. Proximity score (0.0 to 1.0)
            prox_score = max(0.0, 1.0 - (dist_km / assigned_tier.max_km))

            # 2. Heading alignment towards pickup point (0.0 to 1.0)
            heading = item.get('heading_degrees')
            if heading is not None:
                bearing = self.grid.calculate_bearing(lat, lon, pickup_lat, pickup_lon)
                diff = abs(heading - bearing) % 360.0
                if diff > 180.0:
                    diff = 360.0 - diff
                if diff <= 45.0:
                    heading_score = 1.0
                elif diff <= 90.0:
                    heading_score = 0.6
                elif diff <= 135.0:
                    heading_score = 0.2
                else:
                    heading_score = 0.0
            else:
                heading_score = 0.5

            # 3. Idle time fairness / anti-starvation score (0.0 to 1.0)
            idle_minutes = item.get('idle_minutes', 10.0)
            idle_score = min(1.0, max(0.0, idle_minutes / 30.0))

            # 4. Rating & reliability score (0.0 to 1.0)
            raw_rating = item.get('rating', 5.0)
            rating_score = min(1.0, max(0.0, float(raw_rating) / 5.0)) if raw_rating else 1.0

            # Composite weighted dispatch score
            composite_score = (
                0.50 * prox_score
                + 0.20 * heading_score
                + 0.15 * idle_score
                + 0.15 * rating_score
            )

            candidate = DispatchCandidate(
                driver=driver,
                distance_km=dist_km,
                cell_id=cell_id,
                tier=assigned_tier.tier,
                hex_distance=hex_dist,
                score=round(composite_score, 4),
                tier_name=assigned_tier.name,
            )
            candidates_by_tier[assigned_tier.tier].append(candidate)

        # Expanding Ring selection:
        # Step outward through concentric rings until we find candidates.
        for t in self.tiers:
            tier_candidates = candidates_by_tier[t.tier]
            if tier_candidates:
                # Rank candidates: highest composite score first, then lowest distance
                tier_candidates.sort(key=lambda c: (-c.score, c.distance_km))
                return tier_candidates[0]

        return None
