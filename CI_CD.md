CI/CD pipeline README

1.  'Name' - name of the workflow. You can name anything. GitHub displays the names of your workflows on your repository's actions page. If you omit name, GitHub sets it to the workflow file path relative to the root of the repository.

2.  'On' - Workflow triggers. These are events that cause a workflow to run. These events can be:

    - Events that occur in your workflow's repository
    - Events that occur outside of GitHub and trigger a repository_dispatch event on GitHub
    - Scheduled times
    - Manual

    Workflow triggers are defined with the 'on' key. Here the trigger we need is 'push' and 'pull-request' only. We also specify the 'push' to any branch and 'pull-request' to main branch. 

3.  'jobs' - A workflow run is made up of one or more jobs, which run in parallel by default. Each job runs in a runner environment specified by runs-on. You can run an unlimited number of jobs as long as you are within the workflow usage limits. Use jobs.<job_id> to give your job a unique identifier. The key job_id is a string and its value is a map of the job's configuration data. Example:

4.  'needs' - prerequisite job(s). Whenever 'needs' is defined in a job,  'needs' must be performed before this job. In deployment.yml, we define 'needs' as test to make sure tests are passed before the deployment job.

5.  'runs-on' - each job runs in a fresh instance of a virtual environment. Here we choose ubuntu-latest as the instance of the virtual env.

6.  'env' - environment variables. These are available to the steps of all jobs in the workflow. You can also set environment variables that are only available to the steps of a single job or to a single step. Here we list out the working s3 buckets' name, templates' name, stacks' name and AWS region name.

7.  'steps' - Jobs contain a set of steps that will be executed, in order. Each step can be named.

8.  'uses' - for some actions defined by github. 
    -   'actions/checkout@v2': This action checks-out your repository under $GITHUB_WORKSPACE, so your workflow can access it.
    -   'actions/setup-python@v2':  to download, install and set up Python packages from actions/python-versions (need to be specified) that do not come preinstalled on runners.

9.  'run' - to run command on the virtual env. The command must be UNIX command. Here we run command to install dependencies, run unit test, archive the lambda layer packages, deploy the packages and update the Cloud Formation stack. 

Ref: https://docs.github.com/en/actions/using-workflows/triggering-a-workflow