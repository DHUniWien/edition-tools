# edition-tools: Collate an edition from T-PEN

This repository contains the tools and scripts necessary to read manuscript 
transcriptions from T-PEN, convert them into TEI XML, split the text according
to `<milestone>` anchor tags, collate it section by section, and upload it to
a Stemmarest repository of the user's choosing. 

The process is designed to be run as a Github action in a repository dedicated
to the edition.

## Contents

- `Dockerfile` : we use this to build the base image for execution of the 
  workflow, which includes the contents of `tools/` and `scripts/` here. 
  The most recent version is available from the ghcr.io repository.
- `tools/` : the CollateX JAR file and the T-PEN download library
- `scripts/` : the scripts used in the pipeline
- `.github/workflows` : Reusable workflow definitions

## Usage

The following steps describe how to use these tools via Github Actions.
It is possible to use them in a standalone way from the container, though
this would require some examination of the workflow definitions and/or
help messages of the scripts in order to understand their use.

1. Copy the file `backup.yml.dist` to the base level of the edition's 
   repository, and edit it as appropriate. The most important parameters
   are:
   - `username` and `password`: intended for T-PEN username and password.
     If you are running this through Github Actions, then DO NOT change
     these values; they will be automatically replaced with the values in
     your repository secrets (see below)
   - `blacklist`: a list of projects in your T-PEN account that should not
     be included in this collation
   - `keeplist`: a list of files and folders that should not be deleted
     from the `transcription/` folder in your repository.
1. Ensure that your repository has a `transcription/` folder to contain
   the downloaded transcriptions. A further folder `transcription/tei-xml/`
   will be created automatically.
1. (optional) If you wish to customise functions to pass to the 
   [`tpen2tei`](https://pypi.org/project/tpen2tei/) library, specify them 
   in the file `transcription/config.py`. Make sure this file is on the
   keeplist in step 1.
1. Create the following secrets in your repository (under Settings -> Secrets -> Action):
   - `TPEN_USER`: your T-PEN login ID
   - `TPEN_PASS`: your T-PEN login password
   - `SW_PASS`: your Stemmaweb login password
   - `API_HTUSER` (optional): if your Stemmarest instance requires basic HTTP auth, set the username here
   - `API_HTPASS` (optional): if your Stemmarest instance requires basic HTTP auth, set the password here
1. Set up a Github Action in your repository with the following definition:

        name: Pull and upload test collation

        # We run this every day shortly after 2am UTC, or else when invoked manually
        on:
        schedule: 
        - cron: '10 2 * * *'
        workflow_dispatch:
            inputs:
            forceCollate:
                description: "Force the full collation process to run"
                required: true 
                type: boolean
                
        jobs:
        # Call the reusable workflow from DHUniWien/edition_tools.
        download-and-collate:
            name: Pull and collate all transcriptions
            uses: DHUniWien/edition-tools/.github/workflows/download-and-collate.yml@master
            with:
            forceCollate: ${{ inputs.forceCollate }}

            # Set this to true if you want to require all TEI files to be valid
            blockOnValidation: false

            # Set this to the location of your validation schema, relative to the
            # base of your repository
            xml_schema: transcription/tei-xml/tei_all.rng

            # Set this to the endpoint of your Stemmarest repository
            api_test_base: https://example.org/stemmarest

            # Set this to the ID of the Stemmaweb user. If you use Google 
            # authentication, you will need to set this to the long ugly number that 
            # displays in the 'is owned by' field on your existing traditions.
            stemmaweb_user: username@example.com

            # Set these accordingly
            tradition_name: Աղվեսագիրք
            tradition_lang: Armenian
            secrets: inherit

1. Try running it and see what happens! I'm happy to take bug reports.