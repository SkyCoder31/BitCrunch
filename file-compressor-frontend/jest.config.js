const nextJest = require('next/jest');

// Provide the path to your Next.js app to load next.config.js and .env.production
// Environment variables during testing.
const createJestConfig = nextJest({
  dir: './',
});

// Add any custom config to be passed to Jest
/** @type {import('jest').Config} */
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    // Mock CSS imports if not using CSS modules transforms
    // This is important for Next.js projects using CSS modules or global CSS.
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    // Handle module aliases (this will be automatically configured by next/jest)
    // based on the paths in tsconfig.json.
    // Example:
    // '^@/components/(.*)$': '<rootDir>/components/$1',
  },
  // if using TypeScript with a baseUrl set to the root directory then you need the below for alias' to work
  moduleDirectories: ['node_modules', '<rootDir>/'],
};

// createJestConfig is exported this way to ensure that next/jest can load the Next.js config which is async
module.exports = createJestConfig(customJestConfig);
