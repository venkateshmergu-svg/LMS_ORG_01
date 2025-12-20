# LMS Frontend Release Notes

## Version: X.Y.Z
## Release Date: YYYY-MM-DD

---

### Release Information

| Field | Value |
|-------|-------|
| **Version** | `X.Y.Z` |
| **Commit** | `abc123def456...` |
| **Build Number** | `#123` |
| **Build Date** | `2025-01-01T00:00:00Z` |
| **Environment** | Production |

---

### Change Summary

#### Features
- [ ] Feature 1 description
- [ ] Feature 2 description

#### Bug Fixes
- [ ] Fix 1 description
- [ ] Fix 2 description

#### Performance Improvements
- [ ] Improvement 1 description

#### Security Updates
- [ ] Security update 1 description

---

### Breaking Changes

> ⚠️ **Breaking Changes** (if any)

- None / List breaking changes

---

### Dependencies Updated

| Package | Previous | New |
|---------|----------|-----|
| react | 18.2.0 | 18.3.0 |

---

### Deployment Instructions

1. Download release artifact from GitHub Releases
2. Verify `build-manifest.json` matches expected version
3. Deploy to target environment using standard procedure
4. Verify deployment via `/api/health` or version endpoint

---

### Rollback Reference

| Field | Value |
|-------|-------|
| **Previous Version** | `X.Y.Z-1` |
| **Previous Commit** | `prev123...` |
| **Rollback Artifact** | `lms-frontend-X.Y.Z-1.zip` |

**To Rollback:**
1. Trigger the `Frontend Rollback` workflow
2. Specify target version: `X.Y.Z-1`
3. Provide reason and incident ID

---

### Testing Evidence

- [ ] Unit tests passing
- [ ] TypeScript compilation successful
- [ ] ESLint checks passing
- [ ] Build successful
- [ ] UAT sign-off obtained (if required)

---

### Approvals

| Role | Approver | Date |
|------|----------|------|
| Tech Lead | Name | YYYY-MM-DD |
| QA Lead | Name | YYYY-MM-DD |
| Product Owner | Name | YYYY-MM-DD |

---

### Audit Trail

| Timestamp | Action | Actor |
|-----------|--------|-------|
| YYYY-MM-DD HH:MM | Release created | GitHub Actions |
| YYYY-MM-DD HH:MM | Deployed to TEST | Actor Name |
| YYYY-MM-DD HH:MM | UAT approved | Actor Name |
| YYYY-MM-DD HH:MM | Deployed to PROD | Actor Name |
