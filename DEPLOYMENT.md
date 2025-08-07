# Deployment Guide

## Railway (Recommended)

Railway is the easiest platform for deploying this Playwright-based backend.

### Steps:

1. **Connect Repository**
   - Go to [railway.app](https://railway.app)
   - Click "Deploy from GitHub repo"
   - Select this repository

2. **Automatic Detection**
   - Railway will automatically detect the `Dockerfile`
   - The `railway.toml` configures optimal settings

3. **Environment Variables** (Optional)
   - No environment variables required for basic operation
   - All configuration is in the code

4. **Deploy**
   - Railway will build and deploy automatically
   - Build time: ~5-10 minutes (downloading browser binaries)
   - Your API will be available at: `https://your-app.railway.app`

### Railway Benefits:
- ✅ **Playwright support** out of the box
- ✅ **Automatic HTTPS** 
- ✅ **Custom domains** available
- ✅ **Reasonable pricing** for automation workloads
- ✅ **Easy scaling**

## Alternative Platforms

### Google Cloud Run
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/pendo-backend
gcloud run deploy --image gcr.io/PROJECT-ID/pendo-backend --platform managed --memory 2Gi --timeout 900
```

### DigitalOcean App Platform
- Upload this repository
- Select "Docker" as build method
- Set memory to at least 1GB
- Enable HTTP/2

### AWS Lambda (Container)
- Build image: `docker build -t pendo-backend .`
- Push to ECR and deploy as Lambda function
- Set timeout to 15 minutes
- Set memory to 3008MB

## Local Docker Testing

```bash
# Build the image
docker build -t pendo-backend .

# Run locally
docker run -p 8000:8000 pendo-backend

# Test the API
curl http://localhost:8000/health
```

## Production Considerations

1. **Memory**: Minimum 1GB, recommended 2GB
2. **Timeout**: Set to at least 15 minutes for full workflows
3. **CPU**: 1-2 vCPUs recommended for browser automation
4. **Storage**: Ephemeral is fine (stateless architecture)

## Monitoring

- Health check endpoint: `GET /health`
- API info endpoint: `GET /`
- All responses include execution timing 