# Migration Guide: Moving Employee Performance to Production

Use this guide to move the "Employee Performance" app from your test server to your production environment.

## Phase 1: Package the App (on Test Server)

Since your code resides in the `apps/employee_performance` directory, the easiest way is to create a compressed archive of the app.

1.  **Navigate to the apps directory:**
    ```bash
    cd /opt/frappe/Frappe-Production/apps/
    ```
2.  **Compress the app folder:**
    ```bash
    tar -czvf employee_performance.tar.gz employee_performance/
    ```

## Phase 2: Transfer to Production Server

Transfer the file to your new server using `scp` (Secure Copy).

1.  **Run this from your test server:**
    ```bash
    scp employee_performance.tar.gz user@production-ip-address:/tmp/
    ```

## Phase 3: Install on Production (Docker Environment)

If your production server is using the same Docker setup as this one:

1.  **Move the app to the production apps directory:**
    ```bash
    # On production server
    cd /opt/frappe/Frappe-Production/apps/
    cp /tmp/employee_performance.tar.gz .
    tar -xzvf employee_performance.tar.gz
    rm employee_performance.tar.gz
    ```

2.  **Install the app inside the container:**
    ```bash
    # Enter the backend container
    docker exec -it frappe-production-backend-1 bash

    # Run bench commands
    bench get-app /home/frappe/frappe-bench/apps/employee_performance
    bench --site [your-site-name] install-app employee_performance
    
    # Build assets
    bench build --app employee_performance
    ```

3.  **Restart Services:**
    ```bash
    docker restart frappe-production-backend-1
    ```

## Phase 4: Install on Production (Standard Bench)

If your production server is a standard Linux VPS (not Docker):

1.  **Extract the app in `frappe-bench/apps/`**
2.  **Run the following commands:**
    ```bash
    bench get-app /path/to/extracted/employee_performance
    bench --site [your-site-name] install-app employee_performance
    bench build --app employee_performance
    bench restart
    ```

## ⚠️ Important Considerations

*   **Database Migration:** If you created custom fields or modified DocTypes *outside* of the app code, you must migrate those manually or use a database backup.
*   **Dependency Check:** Ensure the `employee_performance` app is listed in your site's `site_config.json`.
*   **Permissions:** After extracting on production, ensure the file owner matches the user running the bench (usually `frappe`).

---
*Generated for Mohammedkh97 — Employee Performance Migration*
