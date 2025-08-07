# EcalsPy

[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<br />
<div align="center">
  <h3 align="center">EcalsPy</h3>

  <p align="center">
    A Python library for syncing EPU calendar with Google Calendar
    <br />
    <a href="https://github.com/nd2204/ecalspy"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/nd2204/ecalspy/issues">Report Bug</a>
    ·
    <a href="https://github.com/nd2204/ecalspy/issues">Request Feature</a>
  </p>
</div>

## About The Project

EcalsPy is a Python library that helps Electric Power University students sync their academic calendar with Google Calendar. It automatically fetches the class schedule from EPU's website and creates corresponding events in Google Calendar.

Key features:

* Automatically fetches class schedules from EPU's website
* Creates Google Calendar events with proper timing and location
* Supports different types of schedules (theory classes, labs, exams)
* Cookie-based authentication for accessing EPU's system

### Built With

* ![Python](https://img.shields.io/badge/python-3.13+-blue.svg)
* [Google Calendar API](https://developers.google.com/calendar)
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/)
* [Requests](https://requests.readthedocs.io/)
* [Browser-Cookie3](https://github.com/borisbabic/browser_cookie3)

## Getting Started

### Prerequisites

* Python 3.13 or higher
* Poetry for dependency management

### Installation

1. Clone the repository

   ```sh
   git clone https://github.com/nd2204/ecalspy.git
   ```

2. Install dependencies using Poetry

   ```sh
   cd ecalspy
   poetry install --no-root
   ```

3. Set up Google Calendar API credentials
   * Go to [Google Cloud Console](https://console.cloud.google.com)
   * Create a new project
   * Enable Google Calendar API
   * Create OAuth 2.0 credentials
   * Download the credentials and paste its content to "GoogleCalendarApiSecret" in `conf.json` (reference from the template `conf-example.json`)

## Usage

1. Make sure you're logged into EPU's website in your browser
2. Run the main script

   ```sh
   poetry run src/main.py
   ```

3. If running for the first time:
   * You'll be prompted to enter your EPU session cookie (if the program can't find the cookies from your browser)
   * A browser window will open for Google Calendar authentication

The script will:

1. Fetch your class schedule for the next week
2. Create corresponding events in your Google Calendar
3. Cache your EPU cookies for future use

## Roadmap

* [x] Basic schedule fetching
* [x] Google Calendar integration
* [ ] Command-line arguments support
* [ ] Multiple week sync
* [ ] Custom event reminder settings
* [ ] GUI interface
* [ ] Login with password

See the [open issues](https://github.com/nd2204/ecalspy/issues) for a full list of proposed features (and known issues).

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

<dn200422@gmail.com>

Project Link: [https://github.com/nd2204/ecalspy](https://github.com/nd2204/ecalspy)

<!-- MARKDOWN LINKS & IMAGES -->
[license-shield]: https://img.shields.io/github/license/nd2204/ecalspy.svg?style=for-the-badge
[license-url]: https://github.com/nd2204/ecalspy/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/nd2204
