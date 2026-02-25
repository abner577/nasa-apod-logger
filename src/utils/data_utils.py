"""
data_utils.py

Utility helpers for formatting and preparing APOD data.
Includes test payloads for when NASA APOD API is down.
"""

import datetime

from src.utils.viewer_utils import build_apod_viewer, viewer_path_to_uri

TEST_DATA = {'resource': {
        'image_set': "apod"
    },
    'concept_tags': "True",
    'date': "2013-10-01",
    'title': "Earth at Night",
    'url': "http://apod.nasa.gov/apod/image/1310/velafilaments_jadescope_960.jpg",
    'explanation': 'The explosion is over but the consequences continue. About eleven thousand years ago a star in the constellation of Vela could be seen to explode. BLAH BLAH BLAH asdhjahsdhgjasd asdh.  ajsdjasdj',
    'concepts': {
        '0': "Astronomy",
        '1': "Star",
        '2': "Sun",
        '3': "Milky Way",
        '4': "Hubble Space Telescope",
        '5': "Earth",
        '6': "Nebula",
        '7': "Interstellar medium"
    }
}

TEST_DATA2 = {'resource': {
        'image_set': "apod"
    },
    'concept_tags': "True",
    'date': "2011-11-02",
    'title': "Filaments of the Vela",
    'url': "https://apod.nasa.gov/apod/image/1707/EarthAtNight_SuomiNPP_1080.jpg",
    'explanation': "Can you find your favorite country or city?  Surprisingly, on this world-wide nightscape, city lights make this task quite possible.  Human-made lights highlight particularly developed or populated areas of the Earth's surface, including the seaboards of Europe, the eastern United States, and Japan.  Many large cities are located near rivers or oceans so that they can exchange goods cheaply by boat.  Particularly dark areas include the central parts of South America, Africa, Asia, and Australia.  The featured composite was created from images that were collected during cloud-free periods in April and October 2012 by the Suomi-NPP satellite, from a polar orbit about 824 kilometers above the surface, using its Visible Infrared Imaging Radiometer Suite (VIIRS).",
    'concepts': {
        '0': "Astronomy",
        '1': "Star",
        '2': "Sun",
        '3': "Milky Way",
        '4': "Hubble Space Telescope",
    }
}

TEST_DATA3 = {
    "copyright": "Panther Observatory",
    "date": "2006-04-15",
    "explanation": "In this stunning cosmic vista, galaxy M81 is on the left surrounded by blue spiral arms.  On the right marked by massive gas and dust clouds, is M82.  These two mammoth galaxies have been locked in gravitational combat for the past billion years.   The gravity from each galaxy dramatically affects the other during each hundred million-year pass.  Last go-round, M82's gravity likely raised density waves rippling around M81, resulting in the richness of M81's spiral arms.  But M81 left M82 with violent star forming regions and colliding gas clouds so energetic the galaxy glows in X-rays.  In a few billion years only one galaxy will remain.",
    "hdurl": "https://apod.nasa.gov/apod/image/0604/M81_M82_schedler_c80.jpg",
    "media_type": "image",
    "service_version": "v1",
    "title": "Galaxy Wars: M81 versus M82",
    "url": "https://apod.nasa.gov/apod/image/0604/M81_M82_schedler_c25.jpg"
  }

TEST_DATA4 = {
    "date": "2013-07-22",
    "explanation": "You are here. Everyone you've ever known is here. Every human who has ever lived -- is here. Pictured above is the Earth-Moon system as captured by the Cassini mission orbiting Saturn in the outer Solar System. Earth is the brighter and bluer of the two spots near the center, while the Moon is visible to its lower right. Images of Earth from Saturn were taken on Friday. Quickly released unprocessed images were released Saturday showing several streaks that are not stars but rather cosmic rays that struck the digital camera while it was taking the image.  The above processed image was released earlier today.  At nearly the same time, many humans on Earth were snapping their own pictures of Saturn.   Note: Today's APOD has been updated.",
    "hdurl": "https://apod.nasa.gov/apod/image/1307/earthmoon2_cassini_946.jpg",
    "media_type": "image",
    "service_version": "v1",
    "title": "Earth and Moon from Saturn",
    "url": "https://apod.nasa.gov/apod/image/1307/earthmoon2_cassini_960.jpg"
  }

TEST_DATA5 = {
    "copyright": "Joe Orman",
    "date": "2000-04-06",
    "explanation": "Rising before the Sun on February 2nd, astrophotographer Joe Orman anticipated this apparition of the bright morning star Venus near a lovely crescent Moon above a neighbor's house in suburban Phoenix, Arizona, USA. Fortunately, the alignment of bright planets and the Moon is one of the most inspiring sights in the night sky and one that is often easy to enjoy and share without any special equipment. Take tonight, for example. Those blessed with clear skies can simply step outside near sunset and view a young crescent Moon very near three bright planets in the west Jupiter, Mars, and Saturn. Jupiter will be the unmistakable brightest star near the Moon with a reddish Mars just to Jupiter's north and pale yellow Saturn directly above. Of course, these sky shows create an evocative picture but the planets and Moon just appear to be near each other -- they are actually only approximately lined up and lie in widely separated orbits. Unfortunately, next month's highly publicized alignment of planets on May 5th will be lost from view in the Sun's glare but such planetary alignments occur repeatedly and pose no danger to planet Earth.",
    "hdurl": "https://apod.nasa.gov/apod/image/0004/vm_orman_big.jpg",
    "media_type": "image",
    "service_version": "v1",
    "title": "Venus, Moon, and Neighbors",
    "url": "https://apod.nasa.gov/apod/image/0004/vm_orman.jpg"
  }

TEST_DATA6 =  {
    "date": "2014-07-12",
    "explanation": "A new star, likely the brightest supernova in recorded human history, lit up planet Earth's sky in the year 1006 AD. The expanding debris cloud from the stellar explosion, found in the southerly constellation of Lupus, still puts on a cosmic light show across the electromagnetic spectrum. In fact, this composite view includes X-ray data in blue from the Chandra Observatory, optical data in yellowish hues, and radio image data in red. Now known as the SN 1006 supernova remnant, the debris cloud appears to be about 60 light-years across and is understood to represent the remains of a white dwarf star. Part of a binary star system, the compact white dwarf gradually captured material from its companion star. The buildup in mass finally triggered a thermonuclear explosion that destroyed the dwarf star. Because the distance to the supernova remnant is about 7,000 light-years, that explosion actually happened 7,000 years before the light reached Earth in 1006. Shockwaves in the remnant accelerate particles to extreme energies and are thought to be a source of the mysterious cosmic rays.",
    "hdurl": "https://apod.nasa.gov/apod/image/1407/sn1006c.jpg",
    "media_type": "image",
    "service_version": "v1",
    "title": "SN 1006 Supernova Remnant",
    "url": "https://apod.nasa.gov/apod/image/1407/sn1006c_c800.jpg"
  }

TEST_DATA7 =  {
    "date": "1997-01-21",
    "explanation": "In Jules Verne's science fiction classic A Journey to the Center of the Earth, Professor Hardwigg and his fellow explorers encounter many strange and exciting wonders. What wonders lie at the center of our Galaxy? Astronomers now know of some of the bizarre objects which exist there, like vast dust clouds,\r bright young stars, swirling rings of gas, and possibly even a large black hole. Much of the Galactic center region is shielded from our view in visible light by the intervening dust and gas. But it can be explored using other forms of electromagnetic radiation, like radio, infrared, X-rays, and gamma rays. This beautiful high resolution image of the Galactic center region in infrared light was made by the SPIRIT III telescope onboard the Midcourse Space Experiment. The center itself appears as a bright spot near the middle of the roughly 1x3 degree field of view, the plane of the Galaxy is vertical, and the north galactic pole is towards the right. The picture is in false color - starlight appears blue while dust is greenish grey, tending to red in the cooler areas.",
    "hdurl": "https://apod.nasa.gov/apod/image/9701/galcen_msx_big.gif",
    "media_type": "image",
    "service_version": "v1",
    "title": "Journey to the Center of the Galaxy \r\nCredit:",
    "url": "https://apod.nasa.gov/apod/image/9701/galcen_msx.jpg"
  }

def format_apod_data(apod_data, build_viewer: bool = True):
    """
      Format raw APOD API data into a normalized snapshot structure.

      Extracts and cleans relevant fields, truncates the explanation,
      and adds a formatted timestamp for logging.

      Args:
      apod_data: Raw APOD response dictionary from the NASA API.

      Returns:
       dict: Formatted APOD snapshot ready for persistence.
    """

    cur_time = datetime.datetime.now()
    cur_time = cur_time.strftime("Day: %m-%d-%Y | Time: %H:%M:%S")

    explanation = apod_data["explanation"].split(".") # makes a list of all the diff sentences, then we just want to return the first 2 sentences
    explanation = explanation[0].strip(" ") + "." + explanation[1] + "." # First we strip off all white space from before the first sentence, then we manually add periods right after each sentence.

    date = apod_data["date"].strip()
    title = apod_data["title"].strip()
    url = apod_data["url"].strip()

    if build_viewer:
        viewer_path = build_apod_viewer({
            "date": date,
            "title": title,
            "url": url,
            "explanation": explanation,
        })
        url_to_store = viewer_path_to_uri(viewer_path)
    else:
        url_to_store = url

    dict_to_return = {
        'date': date,
        'title': title,
        'url': url_to_store,
        'explanation': explanation,
        'logged_at': cur_time,
    }

    return dict_to_return

FORMATTED_TEST_DATA = format_apod_data(TEST_DATA, build_viewer=False)
FORMATTED_TEST_DATA2 = format_apod_data(TEST_DATA2, build_viewer=False)
FORMATTED_TEST_DATA3 = format_apod_data(TEST_DATA3, build_viewer=False)
FORMATTED_TEST_DATA4 = format_apod_data(TEST_DATA4, build_viewer=False)
FORMATTED_TEST_DATA5 = format_apod_data(TEST_DATA5, build_viewer=False)
FORMATTED_TEST_DATA6 = format_apod_data(TEST_DATA6, build_viewer=False)
FORMATTED_TEST_DATA7 = format_apod_data(TEST_DATA7, build_viewer=False)
