# Phase 27 Quick Reference Card

## Build Commands
```bash
npm run dev          # Start development server
npm run build        # Production build (with typecheck)
npm run typecheck    # TypeScript check only
npm run lint         # ESLint check
npm run ci           # All quality gates + build
```

## Environment Files
| File | Environment |
|------|-------------|
| `.env.local` | Local development (gitignored) |
| `.env.development` | Development server |
| `.env.test` | Test/UAT |
| `.env.staging` | Staging |
| `.env.production` | Production |

## CI/CD Workflows
| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `frontend-ci.yml` | Push/PR | Quality gates + build |
| `frontend-release.yml` | Manual | Version bump + release |
| `frontend-rollback.yml` | Manual | Emergency rollback |

## Quality Gates (All Must Pass)
1. ✅ `npm run typecheck` - No TypeScript errors
2. ✅ `npm run lint` - No ESLint warnings
3. ✅ `npm run format:check` - Consistent formatting
4. ✅ `npm run build:only` - Build succeeds

## Artifact Versioning
```
lms-frontend-{version}-{commit}
Example: lms-frontend-1.2.3-abc123f
```

## Rollback (< 15 minutes)
1. Go to Actions → Frontend Rollback
2. Enter target version (e.g., `1.2.2`)
3. Select environment
4. Provide reason (audit requirement)
5. Approve and execute

## Key Files
- `.nvmrc` - Node version (20.18.0)
- `build-manifest.json` - Build metadata (in dist/)
- `PHASE_27_DEPLOYMENT_GUIDE.md` - Full documentation

## Contact
- Build issues → Tech Lead
- Infrastructure → DevOps
- Security → Security Team
