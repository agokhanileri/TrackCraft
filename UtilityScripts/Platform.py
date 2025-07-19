#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 13:44:53 2025

@author: agi
"""

import pandas as pd

# Re-creating the full table structure for export
data = {
    "Category": [
        "JobSearch", "FlightBooking", "HotelBooking", "CarRenting", "ApartmentRenting", "Emails",
        "MusicAdvertisement", "MusicProductionSW", "ShoppingNewItems", "ShoppingUsedItems",
        "SellingSW", "Banking", "StockInvesting", "CryptoInvesting", "SocialMedia",
        "DJSoftware", "VideoEditing", "ImageEditing", "AudioEditing", "UtilityNeeds",
        "Dating", "CodingChallenge", "CodingLearning", "ProjectSharing", "CargoServices",
        "Apparel", "ShoppingGrocery"
    ],
    "Platform": [
        "Indeed (40%, med) > LinkedIn (34%, med) >> Glassdoor (9%, soft) > Monster (6%, soft) > ZipRecruiter (5%, soft)",
        "GoogleFlights (35%, firm) > Expedia (25%, med) > Skyscanner (20%, med) > Kayak (12%, soft) > Hopper (8%, soft)",
        "Booking.com (40%, med) > Expedia (30%, med) >> Hotels.com (12%, soft) > Agoda (10%, med) > Trivago (8%, soft)",
        "Enterprise (40%, med) > Hertz (30%, med) >> Avis (15%, soft) > Turo (10%, firm) > Budget (5%, soft)",
        "Zillow (45%, firm) > Apartments.com (30%, med) >> Rent.com (15%, med) > Craigslist (10%, soft)",
        "Gmail (50%, firm) > Outlook (30%, med) >> Yahoo (10%, soft) > ProtonMail (5%, med) > Zoho (5%, med)",
        "FacebookAds (40%, med) > InstagramAds (30%, firm) >> TikTokAds (20%, firm) > YouTubeAds (10%, med)",
        "AbletonLive (40%, firm) > LogicPro (30%, med) >> ProTools (15%, soft) > FLStudio (10%, med) > Reaper (5%, med)",
        "Amazon (45%, firm) > BestBuy (25%, med) >> Walmart (15%, med) > Target (10%, med) > AliExpress (5%, med)",
        "eBay (40%, med) > Craigslist (30%, soft) >> FacebookMarketplace (20%, firm) > OfferUp (5%, med) > Poshmark (5%, med)",
        "eBay (45%, med) > Craigslist (25%, soft) >> FacebookMarketplace (15%, firm) > OfferUp (10%, med) > Mercari (5%, med)",
        "Chase (40%, firm) > Bank of America (30%, firm) >> Wells Fargo (20%, med) > Citi (5%, med) > CapitalOne (5%, med)",
        "Robinhood (40%, firm) > Webull (30%, med) >> Fidelity (15%, firm) > TD Ameritrade (10%, med) > E*TRADE (5%, med)",
        "Coinbase (40%, firm) > Binance (30%, med) >> Kraken (15%, med) > Gemini (10%, med) > KuCoin (5%, med)",
        "Facebook (25%, soft) > Instagram (30%, firm) >> TikTok (20%, firm) > Twitter (15%, med) > Snapchat (10%, med)",
        "Rekordbox (45%, firm) > Serato (30%, med) >> Traktor (15%, med) > VirtualDJ (10%, med) > djayPro (5%, med)",
        "FinalCutPro (40%, firm) > AdobePremiere (30%, med) >> iMovie (15%, med) > DaVinciResolve (10%, firm) > Filmora (5%, med)",
        "Photoshop (50%, firm) > Lightroom (30%, med) >> Canva (10%, med) > GIMP (5%, med) > Pixelmator (5%, med)",
        "Audacity (40%, med) > LogicPro (30%, firm) >> ProTools (20%, soft) > GarageBand (5%, med) > Reaper (5%, med)",
        "AdobeAcrobat (45%, firm) > Preview (30%, med) >> Foxit (15%, med) > NitroPDF (5%, med) > SmallPDF (5%, med)",
        "Tinder (40%, med) > Bumble (30%, med) >> Hinge (20%, med) > Match (5%, soft) > OkCupid (5%, soft)",
        "LeetCode (40%, firm) > HackerRank (30%, med) >> Codewars (15%, med) > AlgoExpert (10%, med) > TopCoder (5%, med)",
        "Coursera (40%, med) > Udemy (30%, firm) >> edX (15%, med) > KhanAcademy (10%, med) > w3schools (5%, med)",
        "GitHub (50%, firm) > GitLab (30%, med) >> Bitbucket (10%, med) > SourceForge (5%, soft) > Codeberg (5%, soft)",
        "UPS (40%, firm) > FedEx (30%, med) >> USPS (20%, med) > DHL (5%, med) > OnTrac (5%, med)",
        "Nordstrom (40%, med) > Macy's (30%, med) >> Bloomingdale's (15%, med) > Zara (10%, med) > H&M (5%, med)",
        "WholeFoods (40%, med) > Safeway (30%, med) >> Walmart (20%, firm) > TraderJoe's (5%, med) > Kroger (5%, med)"
    ],
    "Need (Essentiality)": [
        "High", "High", "High", "Medium", "High", "High", "High", "High", "High", "Medium",
        "Medium", "High", "High", "High", "Medium", "High", "High", "Medium", "Medium", "High",
        "Medium", "Medium", "Medium", "High", "Medium", "Medium", "Medium"
    ],
    "Cost": [
        "$0", "$0", "$0", "$0", "$0", "$0", "$0", "$199/5yr", "$0", "$0",
        "$0", "$0", "$0", "$0", "$0", "$0", "$299/one-time", "$299/yr", "$0", "$179/yr",
        "$0", "$399/yr", "$399/yr", "$0", "$0", "$0", "$0"
    ]
}

# Convert to a DataFrame
df = pd.DataFrame(data)

# Save to a CSV file for Numbers compatibility
project_path = '/Users/agi/Desktop/Git/PlatformOptimizer/'
df0_name = 'platforms.csv'
df0_path = project_path + df0_name

df.to_csv(df0_path, index=False)

