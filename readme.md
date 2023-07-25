# Web-Based Bike Sharing Application

**Submitted By: Mahesh Srivinay Rayavarapu (msr31)**

This project is a web-based bike sharing application developed as part of my Masters dissertation. The application enables users to easily access and rent bicycles from nearby dock stations. It encompasses both front-end and back-end development, utilizing Django as the web framework, and integrates third-party APIs for secure payment processing and interactive map functionalities.

## Getting Started

To set up the application locally, follow these steps:

1. Download and install Python.
2. Install a Python source code editor (preferably VS Code).
3. Install the project dependencies by running the following command in the terminal: pip install -r requirements.txt
4. Perform database migrations using the following commands: python manage.py makemigrations , python manage.py migrate
5. Run the development server with the following command: python manage.py runserver
The application will be available at http://localhost:8000/.

## Stripe Webhooks Configuration

To access the 'My Pass' page and confirm payments, Stripe webhooks need to be configured in the local environment. Follow these steps to set up the webhooks:

1. Download the Stripe CLI from https://stripe.com/docs/stripe-cli.
2. Open the command prompt and start the Stripe CLI: stripe.exe start
3. Log in to your Stripe account: stripe login
4. Activate the webhook with the following command: stripe listen --forward-to localhost:8000/webhook/

**Note:** Properly configured Stripe webhooks are crucial for viewing the user's pass and confirming payments. Make sure to configure them before calling the Stripe checkout session.

## Project Report

The project report, named "msr31_final_report.pdf," contains detailed information about the development process, challenges faced, and key achievements during my Masters dissertation.

## Project Highlights

- Captivating front-end modules using HTML, Bootstrap CSS, and JavaScript for an intuitive and visually appealing user interface.
- Robust back-end modules using Python on the Django framework for seamless data management and system operations.
- Integration of Google Maps API and TomTom Maps API for real-time information on available dock stations, enhancing user convenience.
- Efficient identification of nearby dock stations using Nominatim Geolocator based on users' locations.
- Secure and seamless payment processing using the Stripe Payments API, supporting various subscription models.
- Utilization of incoming webhooks to trigger specific services upon relevant events for accurate customer interactions.
- Efficient data retrieval from the back-end API using VueJS framework, enhancing application responsiveness and performance.

Feel free to explore the codebase and the project report to learn more about my Masters dissertation project. Enjoy the bike sharing experience on this web-based application!



 

