
echo "Creating environment"

python3 -m venv env

echo "Activating environment"
source env/bin/activate

echo "Installing python dependencies"

python3 -m pip install -r requirements.txt