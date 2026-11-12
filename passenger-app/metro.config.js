const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config');
const fs = require('fs');
const path = require('path');

// Metro is started from the short Z: drive to avoid Windows path-length limits.
// pnpm stores package files through links outside that drive, so resolve Babel's
// generated runtime helpers through the real project location.
const realProjectRoot = fs.realpathSync.native(__dirname);
const workspaceRoot = path.dirname(realProjectRoot);
const babelRuntimeRoot = path.join(
  realProjectRoot,
  'node_modules',
  '@babel',
  'runtime',
);

function resolveBabelRuntime(moduleName) {
  if (
    moduleName !== '@babel/runtime' &&
    !moduleName.startsWith('@babel/runtime/')
  ) {
    return null;
  }

  const relativeModulePath = moduleName.replace('@babel/runtime', '').replace(/^\//, '');
  const basePath = path.join(babelRuntimeRoot, relativeModulePath);
  const candidates = [basePath, `${basePath}.js`, path.join(basePath, 'index.js')];

  return candidates.find(candidate => fs.existsSync(candidate)) ?? null;
}

const config = getDefaultConfig(__dirname);

module.exports = mergeConfig(config, {
  // pnpm's package targets live in the workspace-level .pnpm store.
  watchFolders: [workspaceRoot],
  resolver: {
    // These folders contain generated native/Python cache files. Metro never
    // needs them, and Windows may lock them while Gradle or pytest is running.
    blockList: [/[\\/]\.pytest_cache[\\/].*/, /[\\/]\.gradle[\\/].*/, /[\\/]\.cxx[\\/].*/],
    // The first path is required when this project is opened through Z:.
    // It makes Metro inspect pnpm's real links rather than the SUBST drive.
    nodeModulesPaths: [
      path.join(realProjectRoot, 'node_modules'),
      path.join(workspaceRoot, 'node_modules'),
      path.join(__dirname, 'node_modules'),
    ],
    resolveRequest: (context, moduleName, platform) => {
      const runtimeFile = resolveBabelRuntime(moduleName);

      if (runtimeFile) {
        return { type: 'sourceFile', filePath: runtimeFile };
      }

      return context.resolveRequest(context, moduleName, platform);
    },
  },
});
