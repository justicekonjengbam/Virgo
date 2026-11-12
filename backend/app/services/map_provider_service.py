import logging
from math import asin, cos, radians, sin, sqrt
from urllib.parse import quote

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings
from app.schemas.maps import GeocodedPlaceResponse, MapConfigResponse, RouteResponse

logger = logging.getLogger('virgo.maps')


class MapProviderService:
    api_base = 'https://api.geoapify.com/v1'

    catalog = (
        ('Kangla Fort', 'Kangla, Imphal, Manipur', 24.8115, 93.9422),
        ('Bir Tikendrajit Airport', 'Airport Road, Imphal, Manipur', 24.7600, 93.8967),
        ("Ema Keithel (Mother's Market)", 'Thangal Bazar, Imphal, Manipur', 24.8085, 93.9365),
        ('Regional Institute of Medical Sciences (RIMS)', 'Lamphelpat, Imphal, Manipur', 24.8236, 93.9214),
        ('Manipur University', 'Canchipur, Imphal, Manipur', 24.7533, 93.9280),
        ('JNIMS Porompat', 'Porompat, Imphal East, Manipur', 24.8258, 93.9625),
    )

    @property
    def center_latitude(self) -> float:
        return get_settings().service_center_latitude

    @property
    def center_longitude(self) -> float:
        return get_settings().service_center_longitude

    @property
    def service_radius_km(self) -> float:
        return get_settings().service_radius_km

    @property
    def service_area_name(self) -> str:
        return get_settings().service_area_name

    @property
    def bounds(self) -> list[float]:
        return get_settings().service_bounds

    def config(self) -> MapConfigResponse:
        key = get_settings().geoapify_api_key
        if key:
            return MapConfigResponse(
                style_url=f'https://maps.geoapify.com/v1/styles/klokantech-basic/style.json?apiKey={quote(key)}',
                attribution='© OpenStreetMap contributors · Geoapify',
                service_area=self.bounds,
                service_center=[self.center_longitude, self.center_latitude],
                service_radius_km=self.service_radius_km,
                offline_mode=False,
            )
        if get_settings().environment == 'development':
            logger.info('DEV_OFFLINE_MAP: GEOAPIFY_API_KEY is missing. Using offline MapLibre fallback demo style.')
            return MapConfigResponse(
                style_url='https://demotiles.maplibre.org/style.json',
                attribution='© OpenStreetMap contributors · Virgo Offline Fallback',
                service_area=self.bounds,
                service_center=[self.center_longitude, self.center_latitude],
                service_radius_km=self.service_radius_km,
                offline_mode=True,
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Map services are not configured. Add GEOAPIFY_API_KEY to the backend environment.',
        )

    def search(self, query: str, outstation: bool = False) -> list[GeocodedPlaceResponse]:
        key = get_settings().geoapify_api_key
        if not key:
            if get_settings().environment == 'development':
                return self._offline_catalog_search(query, outstation)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Map services are not configured. Add GEOAPIFY_API_KEY to the backend environment.',
            )

        params = {
            'text': query,
            'format': 'json',
            'lang': 'en',
            'limit': 8,
            'filter': 'countrycode:in' if outstation else f'circle:{self.center_longitude},{self.center_latitude},{round(self.service_radius_km * 1000)}|countrycode:in',
            'bias': f'proximity:{self.center_longitude},{self.center_latitude}',
            'apiKey': key,
        }
        payload = self._get('/geocode/autocomplete', params)
        places = [self._place(item) for item in payload.get('results', []) if item.get('lat') is not None and item.get('lon') is not None and (outstation or self.contains(float(item['lat']), float(item['lon'])))]
        unique: dict[str, GeocodedPlaceResponse] = {}
        for place in places:
            unique.setdefault(place.place_id, place)
        return list(unique.values())

    def reverse(self, latitude: float, longitude: float, outstation: bool = False) -> GeocodedPlaceResponse:
        if not outstation:
            self.ensure_in_service_area(latitude, longitude)

        key = get_settings().geoapify_api_key
        if not key:
            if get_settings().environment == 'development':
                return self._offline_catalog_reverse(latitude, longitude, outstation)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Map services are not configured. Add GEOAPIFY_API_KEY to the backend environment.',
            )

        payload = self._get('/geocode/reverse', {
            'lat': latitude, 'lon': longitude, 'format': 'json', 'lang': 'en',
            'apiKey': key,
        })
        results = payload.get('results', [])
        if not results:
            raise HTTPException(status_code=404, detail='No address was found at this map position.')
        if outstation and str(results[0].get('country_code', '')).lower() != 'in':
            raise HTTPException(status_code=422, detail='Outstation locations must be within India.')
        return self._place(results[0])

    def ensure_in_service_area(self, latitude: float, longitude: float) -> None:
        if not self.contains(latitude, longitude):
            raise HTTPException(status_code=422, detail=f'Choose a location within {int(self.service_radius_km)} km of {self.service_area_name}.')

    def contains(self, latitude: float, longitude: float) -> bool:
        lat1, lon1, lat2, lon2 = map(radians, (self.center_latitude, self.center_longitude, latitude, longitude))
        delta_lat, delta_lon = lat2 - lat1, lon2 - lon1
        value = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
        return 6371.0 * 2 * asin(sqrt(value)) <= self.service_radius_km

    def route(self, origin: tuple[float, float], destination: tuple[float, float]) -> RouteResponse:
        key = get_settings().geoapify_api_key
        if not key:
            if get_settings().environment == 'development':
                return self._offline_route(origin, destination)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Map services are not configured. Add GEOAPIFY_API_KEY to the backend environment.',
            )

        payload = self._get('/routing', {
            'waypoints': f'{origin[0]},{origin[1]}|{destination[0]},{destination[1]}',
            'mode': 'drive', 'traffic': 'approximated', 'format': 'geojson',
            'apiKey': key,
        })
        features = payload.get('features', [])
        if not features:
            raise HTTPException(status_code=422, detail='A drivable route could not be calculated for these locations.')
        feature = features[0]
        properties = feature.get('properties', {})
        return RouteResponse(
            distance_meters=round(float(properties.get('distance', 0))),
            duration_seconds=max(1, round(float(properties.get('time', 0)))),
            geometry=feature.get('geometry', {}),
            toll_fare_paise=0,
            is_estimated=False,
            route_type='road',
        )

    def _distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r_lat1, r_lon1, r_lat2, r_lon2 = map(radians, (lat1, lon1, lat2, lon2))
        d_lat, d_lon = r_lat2 - r_lat1, r_lon2 - r_lon1
        v = sin(d_lat / 2) ** 2 + cos(r_lat1) * cos(r_lat2) * sin(d_lon / 2) ** 2
        return 6371.0 * 2 * asin(sqrt(v))

    def _offline_route(self, origin: tuple[float, float], destination: tuple[float, float]) -> RouteResponse:
        straight_km = self._distance_km(origin[0], origin[1], destination[0], destination[1])
        # Urban road circuity factor ~ 1.3x straight-line
        road_km = max(0.5, round(straight_km * 1.3, 2))
        distance_meters = round(road_km * 1000)
        # Average city speed in Imphal ~ 25 km/h -> 2.4 minutes per km
        duration_seconds = max(60, round(road_km / 25.0 * 3600))
        geometry = {
            'type': 'LineString',
            'coordinates': [
                [origin[1], origin[0]],
                [destination[1], destination[0]],
            ],
        }
        logger.info(
            'DEV_OFFLINE_MAP: Straight-line route estimate used (origin=%s, dest=%s, dist=%s km, duration=%s s)',
            origin, destination, road_km, duration_seconds,
        )
        return RouteResponse(
            distance_meters=distance_meters,
            duration_seconds=duration_seconds,
            geometry=geometry,
            toll_fare_paise=0,
            is_estimated=True,
            route_type='straight_line_estimate',
        )

    def _offline_catalog_search(self, query: str, outstation: bool = False) -> list[GeocodedPlaceResponse]:
        q = query.strip().casefold()
        matches = [
            GeocodedPlaceResponse(
                place_id=f'catalog:{i + 1}',
                name=name,
                formatted_address=address,
                latitude=lat,
                longitude=lon,
            )
            for i, (name, address, lat, lon) in enumerate(self.catalog)
            if q in name.casefold() or q in address.casefold() or q in 'imphal'
        ]
        if not matches:
            matches = [
                GeocodedPlaceResponse(
                    place_id=f'catalog:{i + 1}',
                    name=name,
                    formatted_address=address,
                    latitude=lat,
                    longitude=lon,
                )
                for i, (name, address, lat, lon) in enumerate(self.catalog)
            ]
        return matches[:8]

    def _offline_catalog_reverse(self, latitude: float, longitude: float, outstation: bool = False) -> GeocodedPlaceResponse:
        best = None
        best_dist = float('inf')
        for i, (name, address, lat, lon) in enumerate(self.catalog):
            d = self._distance_km(latitude, longitude, lat, lon)
            if d < best_dist:
                best_dist = d
                best = (i, name, address, lat, lon)
        if best and best_dist < 2.0:
            return GeocodedPlaceResponse(
                place_id=f'catalog:{best[0] + 1}',
                name=best[1],
                formatted_address=best[2],
                latitude=best[3],
                longitude=best[4],
            )
        return GeocodedPlaceResponse(
            place_id=f'offline:{latitude:.4f}:{longitude:.4f}',
            name=f'Location near {self.service_area_name}',
            formatted_address=f'Imphal, Manipur ({latitude:.4f}, {longitude:.4f})',
            latitude=latitude,
            longitude=longitude,
        )

    def _get(self, path: str, params: dict) -> dict:
        try:
            response = httpx.get(
                f'{self.api_base}{path}', params=params, timeout=8.0,
                headers={'User-Agent': f'Virgo/0.1 ({get_settings().maps_contact_email})'},
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Map search is temporarily unavailable. Please try again.',
            ) from exc

    @staticmethod
    def _place(item: dict) -> GeocodedPlaceResponse:
        address = item.get('formatted') or item.get('address_line2') or item.get('name') or 'Selected location'
        name = item.get('name') or item.get('address_line1') or address.split(',')[0]
        place_id = item.get('place_id') or f"geoapify:{item.get('lat')}:{item.get('lon')}"
        return GeocodedPlaceResponse(
            place_id=str(place_id), name=str(name), formatted_address=str(address),
            latitude=float(item['lat']), longitude=float(item['lon']),
        )
