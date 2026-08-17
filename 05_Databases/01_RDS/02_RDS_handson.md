# Practical Guide: Creating, Connecting to, and Deleting an RDS MySQL Database

In this hands-on guide, we will walk through creating a managed MySQL database in Amazon RDS, connecting to it using a desktop SQL client (Sqlectron), running some basic SQL queries, exploring RDS features, and finally securely deleting the instance.

---

## 1. Creating the RDS Database

1. Navigate to the **RDS Console** and click on **Databases** on the left-hand side, then click **Create database**.
2. **Creation Method:** Select **Standard create** (Full configuration) so we can see all the options.
3. **Engine Options:** Select **MySQL**. (Other options include Aurora, PostgreSQL, MariaDB, Oracle, etc.). Leave the engine version as default.
4. **Templates:** Select **Free tier**.
* *Note:* The **Production** template gives you options for Multi-AZ DB instance/cluster deployments (spanning multiple Availability Zones), but we only need a Single-AZ instance for this demo.


5. **Settings:**
* Leave the default database identifier.
* **Master username:** Leave as `admin`.
* **Credentials Management:** Select **Self-managed**. (Using AWS Secrets Manager is more secure but incurs a cost).
* **Master password:** Enter a password (e.g., `password`) and confirm it.


6. **Instance Configuration:** Leave as default (e.g., `db.t4g.micro` or `db.t3.micro`).
7. **Storage:**
* Set to 20 GB.
* *Note:* Under **Additional storage configuration**, **Storage autoscaling** is available. This allows the database to automatically increase storage capacity (e.g., up to 1000 GB) if you run out of space.


8. **Connectivity:**
* Compute resource: Select **Don't connect to an EC2 compute resource**.
* VPC & Subnet: Keep defaults.
* **Public access:** Select **Yes**. (This allows us to connect via our local desktop client using a public IP).
* **VPC security group:** Select **Create new** and name it `demo-rds`.
* Availability Zone & RDS Proxy: Keep defaults/No preference.
* Port: Leave as `3306` (the standard MySQL port).


9. **Additional Configuration:**
* Under **Initial database name**, enter `mydb`.
* Leave monitoring settings (like Enhanced Monitoring) as they are.


10. Click **Create database**. (This process will take a few minutes).

---

## 2. Connecting to the Database via Sqlectron

While the database is spinning up, download and install **Sqlectron** (a GUI-based SQL client).

1. Once your RDS instance status says **Available**, click on the database name to view its details.
2. Copy the **Endpoint** and note the **Port** (`3306`).
3. Click on the Security Group attached to the database and verify the **Inbound Rules**. Ensure that Port 3306 allows traffic from your IP address. *(If you have connection issues, you may temporarily set this to allow anywhere (IPv4), but restrict it in a real-world scenario).*
4. Open **Sqlectron** and add a new database connection:
* **Name:** `RDSDemo`
* **Database Type:** `MySQL`
* **Server Address:** Paste your RDS Endpoint.
* **Port:** `3306`
* **User:** `admin`
* **Password:** `password` (or whatever you set).
* **Initial Database:** `mydb`


5. Click **Test** to ensure the connection is successful, then **Save** and **Connect**.

---

## 3. Running Basic SQL Queries

Once connected to your `mydb` database in Sqlectron, execute the following SQL statements to test your RDS instance.

**Create a Table:**

```sql
CREATE TABLE mytable (
    name VARCHAR(20),
    first_name VARCHAR(20)
);

```

**Insert Data:**

```sql
INSERT INTO mytable (name, first_name) VALUES ('marrek', 'Stephane');

```

**Query the Data:**

```sql
SELECT * FROM mytable;

```

*(This will return a row with the values you just inserted).*

---

## 4. Exploring Managed RDS Features

Back in the AWS RDS Console, you can explore the powerful features that make RDS a fully managed service:

* **Read Replicas:** You can easily create a Read Replica from the Actions menu to scale read capacity.
* **Monitoring:** The Monitoring tab displays critical metrics like CPU Utilization and Database Connection Count, which helps in capacity planning.
* **Snapshots:** You can manually take a snapshot of the database for point-in-time recovery, or migrate the snapshot to a completely different AWS region.
* **Scale Compute:** You can modify the instance type to scale up CPU and RAM as your application grows.

---

## 5. Cleaning Up (Deleting the Database)

To avoid incurring unwanted charges, always delete your resources when finished.

1. Select your database and click **Modify**.
2. Scroll to the very bottom and uncheck **Enable deletion protection** under the Deletion protection settings.
3. Click **Continue** and then **Apply immediately**.
4. Once the modification is complete, select your database again and choose **Actions > Delete**.
5. Uncheck the option to create a final snapshot.
6. Acknowledge the prompt (type `delete me` if asked) confirming that all data will be lost.
7. Click **Delete**.