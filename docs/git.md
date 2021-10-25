# GIT Guidelines

## Development
* Never push into development or master branch. Instead, make a Pull Request.
* Perform work in a `fix/feature` branches.
* Unless stated otherwise in the issue, always branch from the development branch.  The issue should have the tag dependent.

## Creating Branches
* We have two kinds of branches: `feature` and `fix` branches
* `feature` branch are created or new feature requests, functionalities, or enhancements.
* `fix` branches are created for bug fixes


## Naming Conventions
* Branch: *[branch_type]/[issue_number]_[name]*
    * Examples:
        * `feature/5_user_registration`
        * `fix/6_product_detail_bug`

* Commits: *[issue_number] - description*
    * Examples: `120 - Restricted payment endponts for unauthenitcated user`

* Pull Request: *[issue_number] - issue_title*
    * Example: `6 - Product detail bug`

## Creating a Pull Request
* Always keep your fix/feature branch up to date with the development branch.
* Make sure there is code documentation and unit tests when necessary.
* Only modify part of the code that is related to the issue being handled.

## Documentation
* Keep `README.md` updated as a project evolves.
* Comment your code. Try to make it as clear as possible what you are intending with each major section.
* Don't use comments as an excuse for a bad code. Keep your code clean.
* Don't use clean code as an excuse to not comment at all.
* Keep comments relevant as your code evolves.
