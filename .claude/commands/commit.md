# Git Commit Guidelines for Values Compass Project

## Conventional Commit Format

All commits should follow this format:
```
<type>(<scope>): <description>
```

### Commit Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Formatting changes that don't affect code functionality
- `refactor`: Code changes that neither fix bugs nor add features
- `perf`: Performance improvements
- `test`: Adding or improving tests
- `chore`: Changes to build process or auxiliary tools

### Scope (Optional)
The scope provides context about what part of the codebase is affected:
- `visualization`
- `data`
- `analysis`
- `values`
- `scripts`
- `docs`

### Description
- Use imperative, present tense (e.g., "add" not "added" or "adds")
- Don't capitalize the first letter
- No period at the end
- Keep it concise (less than 50 characters)

## Attribution

Always use the `--trailer` flag for attribution instead of including "Generated with" text in the commit body:

```
git commit -m "feat(scope): description" --trailer "Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Examples

```
git commit -m "feat(visualization): add cross-framework value diagram" --trailer "Co-Authored-By: Claude <noreply@anthropic.com>"

git commit -m "fix(data): correct percentages in values hierarchy" --trailer "Co-Authored-By: Claude <noreply@anthropic.com>"

git commit -m "docs(readme): update installation instructions" --trailer "Co-Authored-By: Claude <noreply@anthropic.com>"

git commit -m "style(python): apply black formatting to code" --trailer "Co-Authored-By: Claude <noreply@anthropic.com>"

git commit -m "refactor(analysis): improve clustering algorithm" --trailer "Co-Authored-By: Claude <noreply@anthropic.com>"
```