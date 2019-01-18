python -m venv env
source env/bin/activate
pip install -r ../tests/requirements.txt
touch py_file
in=0
for i in $*; do
    echo $i >> py_file
done
pytest ..
rm py_file
