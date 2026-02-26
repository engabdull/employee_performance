# Migration Guide: Moving Employee Performance via GitHub

Using GitHub is the recommended way to move your app. This makes it easy to install, update, and manage versions on your production server.

## Phase 1: Push the App to GitHub (on Test Server)

1.  **Initialize Git in the app folder:**
    ```bash
    cd /opt/frappe/Frappe-Production/apps/employee_performance/
    git init
    git branch -M main
    ```

2.  **Add and Commit your code:**
    ```bash
    git add .
    git commit -m "Initial commit: Employee Performance Dashboard"
    ```

3.  **Create a New Repository on GitHub:**
    *   Go to [github.com/new](https://github.com/new).
    *   Name it `employee_performance`.
    *   **Do not** initialize with README or License.

4.  **Push to GitHub:**
    *(Replace `YOUR_USERNAME` with your actual GitHub username)*
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/employee_performance.git
    git push -u origin main
    ```

## Phase 2: Install on Production Server

Once your code is on GitHub, installing it on a new server is simple.

### Method A: Docker Environment (Recommended)

1.  **Enter your production backend container:**
    ```bash
    docker exec -it frappe-production-backend-1 bash
    ```

2.  **Download and Install the app:**
    ```bash
    # Replace the URL with your GitHub repo URL
    bench get-app https://github.com/YOUR_USERNAME/employee_performance.git
    
    # Install it on your site
    bench --site [your-site-name] install-app employee_performance
    ```

3.  **Build Assets and Restart:**
    ```bash
    bench build --app employee_performance
    exit
    docker restart frappe-production-backend-1
    ```

### Method B: Standard Linux/Bench Environment

1.  **Run these commands in your `frappe-bench` folder:**
    ```bash
    bench get-app https://github.com/YOUR_USERNAME/employee_performance.git
    bench --site [your-site-name] install-app employee_performance
    bench build --app employee_performance
    bench restart
    ```

---
*Generated for Mohammedkh97 — GitHub Migration workflow*

---
*Generated for Mohammedkh97 — Employee Performance Migration*
