import logging
from django.conf import settings

from mautic import MauticBasicAuthClient, Contacts

logger = logging.getLogger(__name__)


COUNTRIES = {
    "AF": "Afghanistan", "AL": "Albania", "DZ": "Algeria",
    "AD": "Andorra", "AO": "Angola", "AG": "Antigua and Barbuda",
    "AR": "Argentina", "AM": "Armenia", "AU": "Australia",
    "AT": "Austria", "AZ": "Azerbaijan", "BS": "Bahamas",
    "BH": "Bahrain", "BD": "Bangladesh", "BB": "Barbados",
    "BY": "Belarus", "BE": "Belgium", "BZ": "Belize", "BJ": "Benin",
    "BT": "Bhutan", "BO": "Bolivia", "BA": "Bosnia and Herzegovina",
    "BW": "Botswana", "BR": "Brazil", "BN": "Brunei", "BG": "Bulgaria",
    "BF": "Burkina Faso", "BI": "Burundi", "CV": "Cape Verde",
    "KH": "Cambodia", "CM": "Cameroon", "CA": "Canada",
    "CF": "Central African Republic", "TF": "Chad", "CL": "Chile",
    "CN": "China", "CO": "Colombia", "KM": "Comoros",
    "CG": "Republic of the Congo", "CR": "Costa Rica", "HR": "Croatia",
    "CU": "Cuba", "CY": "Cyprus", "CZ": "Czech Republic",
    "DK": "Denmark", "DJ": "Djibouti", "DM": "Dominica",
    "DO": "Dominican Republic",
    "CD": "Democratic Republic of the Congo", "TL": "East Timor",
    "EC": "Ecuador", "EG": "Egypt", "SV": "El Salvador",
    "GQ": "Equatorial Guinea", "ER": "Eritrea", "EE": "Estonia",
    "ET": "Ethiopia", "FJ": "Fiji", "FI": "Finland", "FR": "France",
    "GA": "Gabon", "GM": "Gambia", "GE": "Georgia", "DE": "Germany",
    "GH": "Ghana", "GR": "Greece", "GD": "Grenada", "GT": "Guatemala",
    "GN": "Guinea", "GW": "Guinea Bissau", "GY": "Guyana",
    "HT": "Haiti", "VA": "Holy See", "HN": "Honduras", "HU": "Hungary",
    "IS": "Iceland", "IN": "India", "ID": "Indonesia", "IR": "Iran",
    "IQ": "Iraq", "IE": "Ireland", "IL": "Israel", "IT": "Italy",
    "JM": "Jamaica", "JP": "Japan", "JO": "Jordan", "KZ": "Kazakhstan",
    "KE": "Kenya", "KI": "Kiribati", "KW": "Kuwait", "KG": "Kyrgyzstan",
    "LA": "Laos", "LV": "Latvia", "LB": "Lebanon", "LS": "Lesotho",
    "LR": "Liberia", "LY": "Libya", "LI": "Liechtenstein",
    "LT": "Lithuania", "LU": "Luxembourg", "MG": "Madagascar",
    "MW": "Malawi", "MY": "Malaysia", "MV": "Maldives", "ML": "Mali",
    "MT": "Malta", "MH": "Marshall Islands", "MR": "Mauritania",
    "MU": "Mauritius", "MX": "Mexico", "FM": "Micronesia",
    "MD": "Moldova", "MC": "Monaco", "MN": "Mongolia",
    "ME": "Montenegro", "MA": "Morocco", "MZ": "Mozambique",
    "MM": "Myanmar", "NA": "Namibia", "NR": "Nauru", "NP": "Nepal",
    "NL": "Netherlands", "NZ": "New Zealand", "NI": "Nicaragua",
    "NE": "Niger", "NG": "Nigeria", "KP": "North Korea", "NO": "Norway",
    "OM": "Oman", "PK": "Pakistan", "PW": "Palau", "PA": "Panama",
    "PG": "Papua New Guinea", "PY": "Paraguay", "PE": "Peru",
    "PH": "Philippines", "PL": "Poland", "PT": "Portugal",
    "QA": "Qatar", "RO": "Romania", "RU": "Russia", "RW": "Rwanda",
    "KN": "Saint Kitts and Nevis", "LC": "Saint Lucia", "WS": "Samoa",
    "SM": "San Marino", "ST": "Sao Tome and Principe",
    "SA": "Saudi Arabia", "SN": "Senegal", "RS": "Serbia",
    "SC": "Seychelles", "SL": "Sierra Leone", "SG": "Singapore",
    "SK": "Slovakia", "SI": "Slovenia", "SB": "Solomon Islands",
    "SO": "Somalia", "ZA": "South Africa", "KR": "South Korea",
    "SS": "South Sudan", "ES": "Spain", "LK": "Sri Lanka",
    "VC": "Saint Vincent and the Grenadines", "PS": "Palestine",
    "SD": "Sudan", "SR": "Suriname", "SZ": "Swaziland", "SE": "Sweden",
    "CH": "Switzerland", "SY": "Syria", "TW": "Taiwan",
    "TJ": "Tajikistan", "TZ": "Tanzania", "MK": "Macedonia",
    "TH": "Thailand", "TG": "Togo", "TO": "Tonga",
    "TT": "Trinidad and Tobago", "TN": "Tunisia", "TR": "Turkey",
    "TM": "Turkmenistan", "TV": "Tuvalu", "GB": "United Kingdom",
    "US": "United States", "UG": "Uganda",
    "UA": "Ukraine", "AE": "United Arab Emirates", "UY": "Uruguay",
    "UZ": "Uzbekistan", "VU": "Vanuatu", "VE": "Venezuela",
    "VN": "Vietnam", "YE": "Yemen", "ZM": "Zambia", "ZW": "Zimbabwe"
}


def get_mautic_client():
    if settings.FEATURES.get("MAUTIC_ENABLED"):
        return MauticBasicAuthClient(
            settings.MAUTIC_BASE,
            username=settings.MAUTIC_USERNAME,
            password=settings.MAUTIC_PASSWORD
        )


def register_mautic_contact(user_profile):
    """
    Creates or updates a user record in Mautic DB
    :param user_profile:
    :return:
    """
    client = get_mautic_client()
    if not client:
        return

    user = user_profile.user
    contacts = Contacts(client=client)

    try:
        resp = contacts.create({
            'fullname': user_profile.name,
            'username': user.username,
            'firstname': user.first_name,
            'lastname': user.last_name,
            'verified': 1 if user.is_active else 0,
            'email': user.email,
            'yearofbirth': user_profile.year_of_birth,
            'gender': user_profile.gender_display,
            'levelofeducation': 
                user_profile.level_of_education_display,
            'city': user_profile.city,
            'country': COUNTRIES.get(
                user_profile.country.code, 'Unknown'),
            'goals': user_profile.goals,
        })
    except Exception as e:
        logger.error('Error submitting contact to Mautic')
        logger.exception(e)
        return

    logger.info('User %s has been added successfully to Mautic',
                user.username)
    logger.debug('%s responds successfully with %s',
                 settings.MAUTIC_BASE, resp)

    return resp
