# PhotosynthesisAI
An AI to play the board game Photosynthesis.

# Setting up
`brew install pipx`
`pipx ensurepath`
`pipx install poetry`

(First time setting up) `poetry init`

Add a package with `poetry add numpy`

If manually adding a package to toml or cloning the repo, `poetry install`

Run with 

`cd PhotosynthesisAI`
`poetry run python src/psai/file.py`

To find the env in VSCode, go to the repo in terminal, run
`poetry env info --path`
Then from the palatte choose `Select Python Interpretter` and add that path.