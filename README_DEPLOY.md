# DigitalOcean App Platform Deployment

This app is ready to deploy as a Python web service on DigitalOcean App Platform.

## Files included

- `app.py`: Streamlit dashboard app
- `requirements.txt`: Python dependencies
- `Procfile`: web start command for Streamlit
- `runtime.txt`: Python runtime version
- `.streamlit/config.toml`: Streamlit server settings for cloud hosting
- `.gitignore`: ignores local cache and environment files
- `app.yaml`: optional DigitalOcean App Platform spec

## Recommended App Platform settings

Create a new app from your GitHub repo and use these settings:

- App type: `Web Service`
- Source directory: `/`
- Build command: leave blank
- Run command: `streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT`
- HTTP port: `8080` if DigitalOcean asks for one explicitly, otherwise let the run command use `$PORT`

## Using `app.yaml`

If you prefer infrastructure-as-config, you can deploy with the included `app.yaml`.

Before using it, update:

- `github.repo`
- `github.branch` if your default branch is not `main`

The included spec uses:

- Region: `nyc`
- Instance size: `basic-xxs`
- Port: `8501`

## Notes

- The app expects users to upload the modeling file at runtime, so no dataset needs to be bundled into the deployment.
- If you change the app entrypoint filename, update both `Procfile` and the DigitalOcean run command.

## Local smoke test

```bash
pip install -r requirements.txt
streamlit run app.py
```
