# UIGF-API
Translation API for UIGF-Org, to provide fundamental i18n data for software using UIGF/SRGF standard.

## How to Deploy
- Install [Docker](https://docs.docker.com/engine/install/)
- Modify image name and version in `build.sh` and run it to build docker image
  - You may use `Dockerfile-alpine` instead of `Dockerfile` if you have a more limited disk space
- Create a new database and initial it with `uigf_dict.sql`
- Modify database, network port and App settings in `run.sh`
- Run `run.sh` to start the container

## Live Version
UIGF-API is currently running on [https://api.uigf.org](https://api.uigf.org) and accelerated by [Cloudflare](https://www.cloudflare.com/)

<a href="https://www.cloudflare.com/"><img src="https://uigf.org/CF_logo_stacked_blktype.png"  width="180" height="60"></a>
