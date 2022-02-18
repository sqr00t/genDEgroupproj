
# Final Project

## CREATING A SECURITY GROUP
#### *Tsz-Kin did this for us - can skip*
~

If doing alone:

Before creating your own EC2 instance, you will need to create a security group. Security groups take control of the traffic that is allowed in and out of your instance.

1. Go to EC2 page by using the search bar. On the left-hand side under *Network & Security*, select *Security Groups* and then select *Create security group*.

2. Give your security group a unique name (ours is Team-3) and a description 
3. Under *Inbound rules*, select *Add rule*  

        a. Rule 1: Select SSH for Type and My IP for Source  
        b. Rule 2: Select HTTP for Type and input 0.0.0.0/0 in the text field to the right of Source.

4. Under Outbound rules:

    Select *All TCP* as the type and input "0.0.0.0/0" in the text field to the right of *Destination*.

5. Select *Create security* group to finish.

## EC2 INSTANCE SET-UP 
#### *Tsz-Kin has already done this for us. Skip to ***Accessing EC2 with the CLI****
~

If doing alone:

Go to EC2 and select *Launch Instance*:

**Step 1** - Select *Amazon Linux 2 AMI (HVM), SSD Volume Type*.

**Step 2** - Nothing to do, hit next.

**Step 3** - 

1. For Subnet, select the option which contains the string RedshiftPublicSubnet  
2. For Auto-assign Public IP, select Enable.

**Step 4** - Nothing to do, hit next.

**Step 5** - Nothing to do, hit next.

**Step 6** - 

1. Select an existing security group and select the security group you created. 

2. Select *Review and Launch* and then *Launch*.

3. In the pop-up, select *Create a new key pair* and give it a name (something like "my_name_key")

4. Download the key and launch the instance.

5. Navigate to Instances and select the Instance ID value of your instance.

6. Wait for your instance to have an instance state of Running before moving on. This should only take about 15-30 seconds.

Your instance has now been spun up and is ready to be accessed. Let's see how we can go about getting inside it.

## Connecting to the instance

1. On your Team 3 instance summary page, select Connect in the top-right of the webpage.
2. Select the SSH Client tab and copy the long ssh command under Example. For convenience, ours is:

    `` ssh -i "Team3_key.pem" ec2-user@ec2-52-214-78-181.eu-west-1.compute.amazonaws.com ``
## Accessing EC2 with the CLI 

Now follow the below steps on your terminal (use git bash if on Windows).

1. Download the [Team3_key.pem] Tsz-Kin posted in Discord. 
2. In the folder your downloaded key file is in (most likely "Downloads"), run: 

    ``chmod 400 Team3_key.pem`` 

3. You won't get a message or anything but don't worry. Just paste the ssh command into the terminal and hit enter.:

    ``ssh -i "Team3_key.pem" ec2-user@ec2-52-214-78-181.eu-west-1.compute.amazonaws.com``
 
4. You will be asked Are you sure you want to continue connecting (yes/no/[fingerprint])? , type yes and hit enter. You should now be logged in!

5. Elevate your privileges: 
    
    ``sudo su ``

6. Update all of the packages on the instance: 

   `` yum update -y ``

## Setting up EC2 and Grafana

1. Run the following commands to install and setup Docker:

    ``sudo amazon-linux-extras install docker -y # install``
    
    ``sudo service docker start # start``
    
   `` sudo usermod -a -G docker ec2-user # create new user group``
    
   `` sudo chkconfig docker on # allow docker to run on startup``

2. Setup a Grafana container:

    ``sudo docker run -d -p 80:3000 grafana/grafana``

3. Open a new browser tab and paste your instance's public IPv4 address and hit enter. You can find the public IP4 on the summary page if you click on our team's E3 instance. 

    You will now see your new Grafana board that your whole team can access. Make sure your browser doesn't prepend https to the IP, otherwise it may fail.    
    
    Note: Make sure your port is not occupied with any other container and if you are doing all the steps by yourself, make sure that your security group has an inbound HTTP protocol that allows connecting through Port 80

    Note 2: Your browser may automatically change the URL to HTTPS:// - if it does just remove the S to make it a HTTP connection

## Setup users

To create a new user login for each team member, navigate to *Server Admin --> Users --> New user* and begin creating unique users.

## Connecting Grafana to Cloudwatch
#### *Tsz Kin has done this for us also - all we need to do is download the credentials he posted on discord. This has ACCESS KEY and SECRET ACCESS KEY needed for the next step. Skip to next step.* 
~

Just like in the earlier exercise, we need to connect a data source in order to generate some graphs and metrics.
1. In the AWS console, navigate to IAM --> Users and select Add user .
2. Give the user a name of grafana-team-x (x being the team number) and give it programmatic access.
3. For Permissions , select *Attach existing policies directly*. 
    
    Attach *CloudWatchReadOnlyAccess* and *AmazonEC2ReadOnlyAccess*. 
4. Set the *ScopePermissions permission* boundary.
5. Create the user and keep the success page open. We will need the keys supplied on the page.

## Setting up the Data Source in Grafana 

1. In Grafana, navigate to *Configuration --> Data Sources*. Select *Add data source*, search for Cloudwatch and select.

2. Give it a name. For Authentication Provider, select *Access & secret key*. 

    Paste in both the Access Key ID and Secret Access Key that you can find on the IAM user success page we have open. Leave the IAM role blank

3. Select the default region as eu-west-1 and select Save & Test. 

You should see a confirmation message that it succeeded.

## Creating a Lambda metric
1. Create a new dashboard and add a new panel.
2. Select Cloudwatch as the query type, and Cloudwatch Metrics as the query mode.
3. Select AWS Lambda as the namespace, and Invocations as the metric name.
4. Select Function name as the resource and select the dimension value as your teams ETL lambda. 
5. Update the time query to be last 24 hours or 2/7 days if you need to go back that far to see data being graphed.
6. You should be able to now see how many times your lambda has been invoked over the time elapsed configured for the time period. 

    You can choose different metric options to suit your needs. 

    For example, you can select Error and Duration as the metric name, as well as different stats such as Average, Sum, Min and Max.
    
    As team, think about what kind of monitoring metrics you can establish to display on your new dashboard.






