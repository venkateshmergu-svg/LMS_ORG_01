# ============================================================
# LMS FRONTEND - PHASE 27 DEPLOYMENT GUIDE
# ============================================================
# CI/CD, Environment Strategy, and Release Management
# Version: 1.0.0
# Last Updated: 2025-12-20
# ============================================================

## Table of Contents

1. [Overview](#overview)
2. [Build Contract](#build-contract)
3. [Environment Strategy](#environment-strategy)
4. [CI Pipeline](#ci-pipeline)
5. [Artifact Strategy](#artifact-strategy)
6. [Deployment Procedures](#deployment-procedures)
7. [Rollback Procedures](#rollback-procedures)
8. [Release Traceability](#release-traceability)
9. [Security Considerations](#security-considerations)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide documents the CI/CD, deployment, and release management strategy for the LMS Frontend application. It ensures:

- **Deterministic builds**: Same code produces identical artifacts
- **Environment separation**: Clear boundaries between local/dev/test/prod
- **Quality gates**: Automated enforcement of Definition of Done
- **Fast rollback**: < 15 minutes to restore previous version
- **Audit compliance**: Full traceability of all releases

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CI/CD Pipeline                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐         │
│  │  Commit  │──▶│ Quality  │──▶│  Build   │──▶│ Artifact │         │
│  │          │   │  Gates   │   │          │   │          │         │
│  └──────────┘   └──────────┘   └──────────┘   └────┬─────┘         │
│                                                     │                │
│                      ┌──────────────────────────────┤                │
│                      ▼              ▼               ▼                │
│               ┌──────────┐   ┌──────────┐   ┌──────────┐            │
│               │   DEV    │──▶│  TEST    │──▶│   PROD   │            │
│               │          │   │ (Approval)│   │(Approval)│            │
│               └──────────┘   └──────────┘   └──────────┘            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Build Contract

### Package Manager

- **Manager**: npm (v10.0.0+)
- **Lockfile**: `package-lock.json` (MUST be committed)
- **Install command**: `npm ci` (CI/CD) or `npm install` (local)

### Node.js Version

- **Version**: 20.18.0 (LTS)
- **Specification**: `.nvmrc` file in repository root
- **Enforcement**: `engines` field in `package.json`

```bash
# Local development - use nvm to match version
nvm use

# Verify version
node --version  # Should be v20.18.0
npm --version   # Should be v10.x.x
```

### Build Commands

| Command | Purpose | Usage |
|---------|---------|-------|
| `npm run build` | Full build with type checking | Production builds |
| `npm run build:only` | Vite build only | CI after separate typecheck |
| `npm run typecheck` | TypeScript type checking | Quality gate |
| `npm run lint` | ESLint checking | Quality gate |
| `npm run ci` | All quality gates + build | CI pipeline |

### Build Contract Rules

1. ✅ Single `npm run build` command for all environments
2. ✅ No environment-specific build scripts
3. ✅ Environment values injected via environment variables
4. ✅ Lockfile integrity verified on every build
5. ❌ No `--legacy-peer-deps` or `--force` flags

---

## Environment Strategy

### Environments

| Environment | Purpose | URL Pattern | Auto-Deploy |
|-------------|---------|-------------|-------------|
| **local** | Developer workstation | `localhost:5173` | N/A |
| **development** | Integration testing | `dev.lms.company.com` | Yes (develop branch) |
| **test** | QA & UAT | `test.lms.company.com` | Approval required |
| **staging** | Pre-production mirror | `staging.lms.company.com` | Approval required |
| **production** | Live system | `lms.company.com` | Approval required |

### Environment Variables

All environment variables MUST be prefixed with `VITE_` to be exposed to the frontend.

#### Variable Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `https://api.lms.company.com` |
| `VITE_OAUTH_CLIENT_ID` | OAuth client ID (public) | `lms-frontend-prod` |
| `VITE_OAUTH_AUTHORITY` | OAuth issuer URL | `https://idp.company.com` |
| `VITE_OAUTH_REDIRECT_URI` | OAuth callback URL | `https://lms.company.com/auth/callback` |
| `VITE_FEATURE_*` | Feature flags | `true` / `false` |
| `VITE_APP_NAME` | Application display name | `Leave Management System` |

#### Build-Time Variables (CI/CD Injected)

| Variable | Description | Source |
|----------|-------------|--------|
| `VITE_BUILD_VERSION` | Semantic version | `package.json` |
| `VITE_BUILD_COMMIT` | Git commit SHA | `$GITHUB_SHA` |
| `VITE_BUILD_DATE` | ISO 8601 timestamp | CI build time |
| `VITE_BUILD_NUMBER` | CI build number | `$GITHUB_RUN_NUMBER` |

### Environment Configuration Files

```
frontend/
├── .env.example          # Template with all variables documented
├── .env.local.example    # Local development template
├── .env.development      # Development environment
├── .env.test            # Test/UAT environment
├── .env.staging         # Staging environment
├── .env.production      # Production environment
└── .env.local           # Local overrides (gitignored)
```

### Security Rules

1. ❌ **NO SECRETS** in frontend code or environment files
2. ❌ **NO RUNTIME CONFIG MUTATION** - all values baked at build
3. ✅ OAuth client ID is public (not a secret)
4. ✅ Feature flags are read-only configuration
5. ✅ API base URL points to backend (secrets stay server-side)

---

## CI Pipeline

### Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────┐
│                     CI Pipeline Stages                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. INSTALL          2. TYPECHECK        3. LINT                │
│  ┌──────────┐        ┌──────────┐        ┌──────────┐           │
│  │ npm ci   │───────▶│ tsc      │───────▶│ eslint   │           │
│  │          │        │ --noEmit │        │ --max-   │           │
│  │          │        │          │        │ warnings │           │
│  │          │        │          │        │ 0        │           │
│  └──────────┘        └──────────┘        └──────────┘           │
│       │                   │                   │                  │
│       ▼                   ▼                   ▼                  │
│  ┌──────────┐        ┌──────────┐        ┌──────────┐           │
│  │ Fail on  │        │ Fail on  │        │ Fail on  │           │
│  │ lockfile │        │ ANY TS   │        │ ANY      │           │
│  │ mismatch │        │ error    │        │ warning  │           │
│  └──────────┘        └──────────┘        └──────────┘           │
│                                                                  │
│  4. BUILD            5. ARTIFACT                                 │
│  ┌──────────┐        ┌──────────┐                               │
│  │ vite     │───────▶│ Upload   │                               │
│  │ build    │        │ artifact │                               │
│  │          │        │ + hash   │                               │
│  └──────────┘        └──────────┘                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Quality Gates (Mandatory)

| Gate | Command | Failure Condition |
|------|---------|-------------------|
| TypeScript | `npm run typecheck` | Any type error |
| ESLint | `npm run lint` | Any warning or error |
| Prettier | `npm run format:check` | Any formatting issue |
| Build | `npm run build:only` | Build failure |

### CI Rules

1. ✅ All quality gates MUST pass before merge
2. ✅ CI failure blocks PR merge
3. ❌ No manual overrides without documented exception
4. ✅ All PRs require CI pass + code review
5. ✅ Protected branches enforce CI status checks

### GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `frontend-ci.yml` | Push/PR | Quality gates + build |
| `frontend-release.yml` | Manual | Version bump + release |
| `frontend-rollback.yml` | Manual | Emergency rollback |

---

## Artifact Strategy

### Artifact Naming

```
lms-frontend-{version}-{short_commit}
```

Example: `lms-frontend-1.2.3-abc123f`

### Artifact Contents

```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js      # Main bundle
│   ├── vendor-[hash].js     # React, React-DOM, Router
│   ├── query-[hash].js      # React Query
│   ├── utils-[hash].js      # date-fns, axios, clsx
│   └── index-[hash].css     # Styles
└── build-manifest.json      # Build metadata
```

### Build Manifest

Every artifact includes `build-manifest.json`:

```json
{
  "version": "1.2.3",
  "commit": "abc123def456...",
  "shortCommit": "abc123d",
  "buildNumber": "456",
  "buildDate": "2025-01-15T10:30:00Z",
  "branch": "main",
  "workflow": "frontend-ci",
  "runId": "12345678"
}
```

### Artifact Lifecycle

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Build   │────▶│  Store   │────▶│ Promote  │────▶│ Archive  │
│          │     │ (30 days)│     │          │     │ (90 days)│
└──────────┘     └──────────┘     └──────────┘     └──────────┘
                      │
                      ▼
              ┌──────────────────────────────────────┐
              │         Promotion Path               │
              │   DEV ──▶ TEST ──▶ STAGING ──▶ PROD  │
              │   (same artifact, no rebuild)        │
              └──────────────────────────────────────┘
```

### Immutability Rules

1. ✅ **Build once, deploy many**: Same artifact to all environments
2. ❌ **No rebuilding per environment**
3. ✅ Environment config via env vars at build time
4. ✅ Artifact content hash included in filenames
5. ✅ Version + commit = unique artifact identifier

---

## Deployment Procedures

### Static Hosting (Preferred)

```bash
# Example: AWS S3 + CloudFront deployment
aws s3 sync dist/ s3://lms-frontend-${ENV}/ \
  --delete \
  --cache-control "public, max-age=31536000, immutable" \
  --exclude "index.html" \
  --exclude "build-manifest.json"

aws s3 cp dist/index.html s3://lms-frontend-${ENV}/ \
  --cache-control "no-cache, no-store, must-revalidate"

aws cloudfront create-invalidation \
  --distribution-id ${CLOUDFRONT_DIST_ID} \
  --paths "/index.html" "/build-manifest.json"
```

### Container Hosting (If Required)

```dockerfile
# Dockerfile
FROM nginx:alpine

COPY dist/ /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Deployment Checklist

- [ ] Artifact version matches release notes
- [ ] Build manifest verified
- [ ] Environment variables confirmed
- [ ] CDN cache invalidated (if applicable)
- [ ] Health check passing
- [ ] Version visible in deployed app

### Manual Approval Gates

| Environment | Approvers | SLA |
|-------------|-----------|-----|
| Development | Auto-deploy | N/A |
| Test | Tech Lead | 1 hour |
| Staging | Tech Lead + QA Lead | 4 hours |
| Production | Tech Lead + Product Owner | Business hours only |

---

## Rollback Procedures

### Rollback Criteria

Initiate rollback if:
- Critical bug affecting users
- Security vulnerability discovered
- Performance degradation > 50%
- Compliance/audit issue

### Rollback Process

#### Option 1: GitHub Actions (Recommended)

1. Navigate to Actions → Frontend Rollback
2. Click "Run workflow"
3. Enter:
   - Target version (e.g., `1.2.2`)
   - Environment (e.g., `production`)
   - Reason (required for audit)
   - Incident ID (if applicable)
4. Approve deployment
5. Verify rollback

#### Option 2: Manual (Emergency)

```bash
# 1. Identify previous artifact
PREV_VERSION="1.2.2"

# 2. Download from artifact storage
aws s3 cp s3://lms-artifacts/lms-frontend-${PREV_VERSION}.zip ./

# 3. Deploy
unzip lms-frontend-${PREV_VERSION}.zip -d dist/
aws s3 sync dist/ s3://lms-frontend-prod/ --delete

# 4. Invalidate CDN
aws cloudfront create-invalidation \
  --distribution-id ${DIST_ID} \
  --paths "/*"

# 5. Verify
curl -s https://lms.company.com/build-manifest.json | jq '.version'
```

### Rollback SLA

| Metric | Target |
|--------|--------|
| Detection to decision | < 5 minutes |
| Rollback execution | < 10 minutes |
| **Total rollback time** | **< 15 minutes** |

### Post-Rollback Actions

1. ✅ Verify application health
2. ✅ Notify stakeholders
3. ✅ Create incident report
4. ✅ Root cause analysis
5. ❌ No hotfixes in production - fix forward in next release

---

## Release Traceability

### Version Visibility

The build version is visible in:

1. **UI Footer** (all pages)
2. **Admin > System Info** page
3. **Build manifest** (`/build-manifest.json`)
4. **Browser console** (on app load)

### Version Format

```
Full: 1.2.3+abc123d.456
      │   │       │
      │   │       └── Build number
      │   └────────── Short commit hash
      └────────────── Semantic version
```

### Answering "What version was running at time X?"

1. **Check deployment logs**: GitHub Actions deployment history
2. **Check artifact storage**: Timestamped artifacts with manifests
3. **Check monitoring**: Version metrics/tags in monitoring system
4. **Check audit logs**: Deployment audit records

### Release Notes

Every release includes:
- Version number
- Commit hash
- Build date
- Change summary
- Rollback reference

Template: `RELEASE_NOTES_TEMPLATE.md`

---

## Security Considerations

### Frontend Security Rules

| Rule | Enforcement |
|------|-------------|
| No secrets in code | Code review + scanning |
| No hardcoded URLs | Environment variables |
| CSP headers | CDN/server configuration |
| HTTPS only | Infrastructure |
| Dependency scanning | npm audit in CI |

### Dependency Management

```bash
# Check for vulnerabilities
npm audit

# Update dependencies (patch only in prod)
npm update

# Check outdated packages
npm outdated
```

---

## Troubleshooting

### Common Issues

#### Build Fails: Lockfile Mismatch

```bash
# Error: The lockfile is out of sync...
# Solution: Regenerate lockfile
rm -rf node_modules package-lock.json
npm install
git add package-lock.json
git commit -m "chore: update lockfile"
```

#### Build Fails: TypeScript Error

```bash
# Run typecheck locally to see errors
npm run typecheck

# Check specific file
npx tsc --noEmit src/path/to/file.ts
```

#### Environment Variable Not Found

```bash
# Verify variable is prefixed with VITE_
# Check .env file is loaded
# Restart dev server after .env changes
npm run dev
```

#### CDN Cache Issues

```bash
# Force full invalidation
aws cloudfront create-invalidation \
  --distribution-id ${DIST_ID} \
  --paths "/*"
```

---

## Quick Reference

### Commands

```bash
# Development
npm run dev         # Start dev server
npm run build       # Full production build
npm run preview     # Preview production build

# Quality checks
npm run typecheck   # TypeScript check
npm run lint        # ESLint check
npm run format      # Format code

# CI simulation
npm run ci          # Run all quality gates
```

### Files

| File | Purpose |
|------|---------|
| `.nvmrc` | Node.js version |
| `.npmrc` | npm configuration |
| `.env.*` | Environment configuration |
| `vite.config.ts` | Build configuration |
| `build-manifest.json` | Build metadata (in dist/) |

### Contacts

| Role | Responsibility |
|------|----------------|
| Tech Lead | Build/deploy issues |
| DevOps | Infrastructure/CDN |
| Security | Vulnerability response |

---

*This document is maintained as part of Phase 27 - Frontend Deployment & CI/CD Strategy.*
