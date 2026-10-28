import js from '@eslint/js';
import globals from 'globals';
import react from 'eslint-plugin-react';
export default [{
  files: ['server/frontend/src/**/*.js', 'server/frontend/src/**/*.jsx'],
  languageOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
    parserOptions: {ecmaFeatures: {jsx: true}},
    globals: globals.browser
  },
  plugins: {react},
  settings: {react: {version: '18.3'}},
  rules: {
    ...js.configs.recommended.rules,
    'react/jsx-uses-react': 'error',
    'react/jsx-uses-vars': 'error'
  }
}];
