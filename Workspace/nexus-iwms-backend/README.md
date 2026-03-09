# Nexus IWMS Backend

A Node.js backend API for Project Nexus IWMS built with Express.js and TypeScript.

## Features

- JWT-based authentication
- Role-Based Access Control (RBAC)
- Database models for users, roles, permissions
- OpenAPI/Swagger documentation
- Basic system settings management

## Setup

1. Clone the repository
2. Install dependencies: `npm install`
3. Copy `.env.example` to `.env` and fill in the values
4. Start MongoDB (if using local)
5. Run in development: `npm run dev`
6. Build and start: `npm run build && npm start`

## Scripts

- `npm run dev`: Start development server with ts-node
- `npm run build`: Compile TypeScript to JavaScript
- `npm start`: Start production server
- `npm test`: Run tests

## API Documentation

Swagger docs available at `/api-docs` when server is running.