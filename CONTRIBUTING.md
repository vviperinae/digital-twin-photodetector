# Contributing Workflow

1. Pull latest main: `git checkout main && git pull`
2. Create a feature branch: `git checkout -b feature/<your-name>-<short-desc>`
   e.g. `feature/alice-grafana-dashboard`
3. Commit small, frequent changes with clear messages:
   `git commit -m "Add fault classifier unit tests"`
4. Push your branch: `git push -u origin feature/<your-name>-<short-desc>`
5. Open a Pull Request into `main` on GitHub
6. At least 1 teammate reviews and approves
7. Merge via "Squash and merge" at end of each sprint
8. Delete the branch after merge
