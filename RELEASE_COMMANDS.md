# v2.0.0 Release Commands - Quick Reference

**Status**: Ready to execute
**Last Updated**: 2025-12-12

---

## 🚀 Step-by-Step Release Commands

### Step 1: Push to GitHub

```bash
# Verify current branch and commits
git status
git log --oneline -3

# Push main branch
git push origin main

# Push v2.0.0 tag
git push origin v2.0.0

# Verify push
git branch -r -v
git tag -l -n 1 | grep v2.0.0
```

**Expected Result**: Both main branch and v2.0.0 tag appear on GitHub

---

### Step 2: Publish Python Package to PyPI

```bash
# Navigate to Python package directory
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/packages/python

# Verify build artifacts exist
ls -lh dist/

# Install twine if not already installed
pip install twine

# Upload to PyPI (will prompt for credentials)
twine upload dist/*

# Verify package on PyPI
pip install prompt-enhancement --upgrade
prompt-enhance-verify
```

**Expected Result**: Package appears on https://pypi.org/project/prompt-enhancement/

**PyPI Credentials**: Use your PyPI API token
- Visit: https://pypi.org/manage/account/tokens/
- Create new token if needed
- When prompted by twine: use `__token__` as username, token as password

---

### Step 3: Publish NPM Package to Registry

```bash
# Navigate to NPM package directory
cd /home/sunrise/Prompt-Enhancement-Auggie/Prompt-Enhancement/packages/npm

# Verify package.json has version 2.0.0
cat package.json | grep version

# Login to NPM (first time only)
npm login
# Follow prompts to authenticate with your NPM account

# Publish package
npm publish

# Verify package on NPM
npm view @jodykwong/prompt-enhancement
npm install -g @jodykwong/prompt-enhancement@latest
prompt-enhance-verify
```

**Expected Result**: Package appears on https://www.npmjs.com/package/@jodykwong/prompt-enhancement

**NPM Credentials**: Use your NPM account credentials
- Create account at: https://www.npmjs.com/signup
- Enable 2FA for security (optional but recommended)

---

### Step 4: Create GitHub Release

#### Option A: Using GitHub CLI (Recommended)

```bash
# Create release from release notes
gh release create v2.0.0 \
  --title "v2.0.0 - Comprehensive Cross-Project Deployment System" \
  --notes "$(cat RELEASE_NOTES.md)"

# Verify release created
gh release view v2.0.0
```

#### Option B: Manual via GitHub Web UI

1. Visit: https://github.com/jodykwong/Prompt-Enhancement/releases/new
2. Select tag: `v2.0.0`
3. Release title: `v2.0.0 - Comprehensive Cross-Project Deployment System`
4. Description: Copy content from `RELEASE_NOTES.md`
5. Check: "This is a pre-release" (if applicable)
6. Click: "Publish release"

**Expected Result**: GitHub release page with full release notes

---

### Step 5: Update Project Metadata

#### GitHub Project Settings

```bash
# Update via GitHub web UI:
# https://github.com/jodykwong/Prompt-Enhancement/settings

# 1. Update Description
# Old: "AI-powered prompt enhancement tool for development workflows"
# New: "v2.0.0 - Cross-project AI prompt enhancement library available on PyPI and NPM"

# 2. Add Topics (Tags)
# - prompt-engineering
# - ai
# - claude-code
# - deployment
# - python
# - javascript
# - automation
```

#### Update README Links (if needed)

```bash
# Verify all links in main README.md
grep -n "pypi.org\|npmjs.com" README.md

# Expected URLs:
# - https://pypi.org/project/prompt-enhancement/
# - https://www.npmjs.com/package/@jodykwong/prompt-enhancement
```

---

### Step 6: Publish Release Announcements (Optional)

#### GitHub Discussions

```bash
# Create discussion announcement
gh discussion create \
  --title "🎉 Prompt Enhancement v2.0.0 Released!" \
  --body "$(cat RELEASE_NOTES.md)"
```

#### Social Media & Communities

```bash
# Suggested platforms:
# - Twitter/X: Tag @anthropic, mention Claude Code
# - Reddit: r/Python, r/node, r/opensource
# - HackerNews: Submit to "Show HN"
# - Dev.to: Publish article
```

---

## 📋 Pre-Release Checklist

Before starting the release:

- [ ] Git commits pushed from local
- [ ] Git tag v2.0.0 created locally
- [ ] Python package built (dist/ folder has .tar.gz and .whl)
- [ ] All version numbers consistent (setup.py, pyproject.toml, package.json)
- [ ] RELEASE_NOTES.md updated
- [ ] CHANGELOG.md updated
- [ ] Documentation complete

Before publishing to PyPI:

- [ ] PyPI account created: https://pypi.org/account/register/
- [ ] PyPI API token generated: https://pypi.org/manage/account/tokens/
- [ ] Twine installed: `pip install twine`
- [ ] Package builds successfully: `python3 -m build`
- [ ] No errors in build output

Before publishing to NPM:

- [ ] NPM account created: https://www.npmjs.com/signup
- [ ] Logged in locally: `npm login`
- [ ] Package name unique on NPM Registry
- [ ] package.json is valid JSON
- [ ] Scripts folder exists with correct files

---

## ✅ Post-Release Verification

### Python Package Verification

```bash
# Install from PyPI
pip install prompt-enhancement

# Verify CLI commands available
prompt-enhance-install --help
prompt-enhance-setup --help
prompt-enhance-verify --help

# Test installation on another project
prompt-enhance-install /path/to/test/project
cd /path/to/test/project
prompt-enhance-verify
```

### NPM Package Verification

```bash
# Install from NPM
npm install -g @jodykwong/prompt-enhancement

# Verify CLI commands available
prompt-enhance-install --help
prompt-enhance-setup --help
prompt-enhance-verify --help

# Test installation on another project
prompt-enhance-install /path/to/test/project
cd /path/to/test/project
prompt-enhance-verify
```

### GitHub Verification

```bash
# Check releases page
open https://github.com/jodykwong/Prompt-Enhancement/releases

# Check git tag
git tag -l v2.0.0 -n 5
```

---

## 🆘 Troubleshooting

### PyPI Upload Issues

**Error**: "HTTP 403: User not authenticated"
```bash
# Solution: Check API token validity
# https://pypi.org/manage/account/tokens/
# Delete and recreate token if needed
```

**Error**: "Package version already exists"
```bash
# Solution: Version conflict (usually won't happen with new version)
# Verify version in setup.py and pyproject.toml
python3 -m build  # Will fail with version error
```

### NPM Publish Issues

**Error**: "You must be logged in to publish packages"
```bash
# Solution: Authenticate with NPM
npm login
npm whoami  # Verify logged in
```

**Error**: "Package name is not available"
```bash
# Solution: Try different package name or verify ownership
npm view @jodykwong/prompt-enhancement
```

### Git Push Issues

**Error**: "fatal: could not read Username"
```bash
# Solution: Configure git credentials
git config --global user.email "jodykwong@example.com"
git config --global user.name "Jody Kwong"
# Or use SSH instead of HTTPS
```

---

## 📞 Support Resources

- **PyPI Docs**: https://packaging.python.org/
- **NPM Docs**: https://docs.npmjs.com/
- **GitHub Docs**: https://docs.github.com/
- **Twine Docs**: https://twine.readthedocs.io/

---

## 🎯 Summary

**Total Steps**: 6 major steps
**Estimated Time**:
- Steps 1-3 (core release): 10-15 minutes
- Step 4 (GitHub Release): 5 minutes
- Step 5 (metadata): 5 minutes
- Step 6 (announcements): Optional

**Success Criteria**:
- ✅ Code and tag pushed to GitHub
- ✅ Python package published to PyPI
- ✅ NPM package published to NPM Registry
- ✅ GitHub Release created with notes
- ✅ Package managers list v2.0.0

---

**Ready to Release!** 🚀

*Follow commands in order. Each step is independent and can be verified immediately.*

---

*v2.0.0 Release - Quick Reference Guide*
*Generated: 2025-12-12*
