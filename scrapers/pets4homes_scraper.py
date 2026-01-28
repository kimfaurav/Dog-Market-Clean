#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random
import os
import re
from datetime import datetime

class Pets4HomesScraper:
    
    BREED_URLS = {
        'Affenpinscher': 'https://www.pets4homes.co.uk/sale/puppies/affenpinscher/',
        'Afghan Hound': 'https://www.pets4homes.co.uk/sale/puppies/afghan-hound/',
        'Airedale Terrier': 'https://www.pets4homes.co.uk/sale/puppies/airedale-terrier/',
        'Akita': 'https://www.pets4homes.co.uk/sale/puppies/akita/',
        'Japanese Akita Inu': 'https://www.pets4homes.co.uk/sale/puppies/japanese-akita-inu/',
        'Alapaha Blue Blood Bulldog': 'https://www.pets4homes.co.uk/sale/puppies/alapaha-blue-blood-bulldog/',
        'Alaskan Malamute': 'https://www.pets4homes.co.uk/sale/puppies/alaskan-malamute/',
        'American Bulldog': 'https://www.pets4homes.co.uk/sale/puppies/american-bulldog/',
        'American Bully': 'https://www.pets4homes.co.uk/sale/puppies/american-bully/',
        'American Cocker Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/american-cocker-spaniel/',
        'American Bull Staffy': 'https://www.pets4homes.co.uk/sale/puppies/american-bull-staffy/',
        'Anatolian Shepherd': 'https://www.pets4homes.co.uk/sale/puppies/anatolian-shepherd/',
        'Aussiedoodle': 'https://www.pets4homes.co.uk/sale/puppies/aussiedoodle/',
        'Australian Cattle Dog': 'https://www.pets4homes.co.uk/sale/puppies/australian-cattle-dog/',
        'Australian Kelpie': 'https://www.pets4homes.co.uk/sale/puppies/australian-kelpie/',
        'Australian Labradoodle': 'https://www.pets4homes.co.uk/sale/puppies/australian-labradoodle/',
        'Australian Shepherd': 'https://www.pets4homes.co.uk/sale/puppies/australian-shepherd/',
        'Australian Silky Terrier': 'https://www.pets4homes.co.uk/sale/puppies/australian-silky-terrier/',
        'Australian Terrier': 'https://www.pets4homes.co.uk/sale/puppies/australian-terrier/',
        'Azawakh': 'https://www.pets4homes.co.uk/sale/puppies/azawakh/',
        'Bandog': 'https://www.pets4homes.co.uk/sale/puppies/bandog/',
        'Barbet': 'https://www.pets4homes.co.uk/sale/puppies/barbet/',
        'Basenji': 'https://www.pets4homes.co.uk/sale/puppies/basenji/',
        'Basset Bleu De Gascogne': 'https://www.pets4homes.co.uk/sale/puppies/basset-bleu-de-gascogne/',
        'Basset Fauve de Bretagne': 'https://www.pets4homes.co.uk/sale/puppies/basset-fauve-de-bretagne/',
        'Basset Hound': 'https://www.pets4homes.co.uk/sale/puppies/basset-hound/',
        'Bavarian Mountain Hound': 'https://www.pets4homes.co.uk/sale/puppies/bavarian-mountain-hound/',
        'Beagle': 'https://www.pets4homes.co.uk/sale/puppies/beagle/',
        'Beaglier': 'https://www.pets4homes.co.uk/sale/puppies/beaglier/',
        'Bearded Collie': 'https://www.pets4homes.co.uk/sale/puppies/bearded-collie/',
        'Beauceron': 'https://www.pets4homes.co.uk/sale/puppies/beauceron/',
        'Bedlington Terrier': 'https://www.pets4homes.co.uk/sale/puppies/bedlington-terrier/',
        'Belgian Shepherd Dog': 'https://www.pets4homes.co.uk/sale/puppies/belgian-shepherd-dog/',
        'Bergamasco': 'https://www.pets4homes.co.uk/sale/puppies/bergamasco/',
        'Bernedoodle': 'https://www.pets4homes.co.uk/sale/puppies/bernedoodle/',
        'Bernese Mountain Dog': 'https://www.pets4homes.co.uk/sale/puppies/bernese-mountain-dog/',
        'Bichon Frise': 'https://www.pets4homes.co.uk/sale/puppies/bichon-frise/',
        'Biewer Terrier': 'https://www.pets4homes.co.uk/sale/puppies/biewer-terrier/',
        'Russian Black Terrier': 'https://www.pets4homes.co.uk/sale/puppies/russian-black-terrier/',
        'Bloodhound': 'https://www.pets4homes.co.uk/sale/puppies/bloodhound/',
        'Bocker': 'https://www.pets4homes.co.uk/sale/puppies/bocker/',
        'Boerboel': 'https://www.pets4homes.co.uk/sale/puppies/boerboel/',
        'Bolognese': 'https://www.pets4homes.co.uk/sale/puppies/bolognese/',
        'Borador': 'https://www.pets4homes.co.uk/sale/puppies/borador/',
        'Border Collie': 'https://www.pets4homes.co.uk/sale/puppies/border-collie/',
        'Border Terrier': 'https://www.pets4homes.co.uk/sale/puppies/border-terrier/',
        'Bordoodle': 'https://www.pets4homes.co.uk/sale/puppies/bordoodle/',
        'Borzoi': 'https://www.pets4homes.co.uk/sale/puppies/borzoi/',
        'Boston Terrier': 'https://www.pets4homes.co.uk/sale/puppies/boston-terrier/',
        'Bouvier Des Flandres': 'https://www.pets4homes.co.uk/sale/puppies/bouvier-des-flandres/',
        'Boxer': 'https://www.pets4homes.co.uk/sale/puppies/boxer/',
        'Bracco Italiano': 'https://www.pets4homes.co.uk/sale/puppies/bracco-italiano/',
        'Braque dAuvergne': 'https://www.pets4homes.co.uk/sale/puppies/braque-dauvergne/',
        'Braque du Bourbonnais': 'https://www.pets4homes.co.uk/sale/puppies/braque-du-bourbonnais/',
        'Briard': 'https://www.pets4homes.co.uk/sale/puppies/briard/',
        'Brittany Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/brittany-spaniel/',
        'Bull Terrier': 'https://www.pets4homes.co.uk/sale/puppies/bull-terrier/',
        'English Bull Terrier': 'https://www.pets4homes.co.uk/sale/puppies/english-bull-terrier/',
        'Miniature Bull terrier': 'https://www.pets4homes.co.uk/sale/puppies/miniature-bull-terrier/',
        'English Bulldog': 'https://www.pets4homes.co.uk/sale/puppies/english-bulldog/',
        'Bullmastiff': 'https://www.pets4homes.co.uk/sale/puppies/bullmastiff/',
        'Cairn Terrier': 'https://www.pets4homes.co.uk/sale/puppies/cairn-terrier/',
        'Caledonian wolfalike': 'https://www.pets4homes.co.uk/sale/puppies/caledonian-wolfalike/',
        'Canaan Dog': 'https://www.pets4homes.co.uk/sale/puppies/canaan-dog/',
        'Canadian Eskimo Dog': 'https://www.pets4homes.co.uk/sale/puppies/canadian-eskimo-dog/',
        'Cane Corso': 'https://www.pets4homes.co.uk/sale/puppies/cane-corso/',
        'Welsh Corgi Cardigan': 'https://www.pets4homes.co.uk/sale/puppies/welsh-corgi-cardigan/',
        'Catalan Sheepdog': 'https://www.pets4homes.co.uk/sale/puppies/catalan-sheepdog/',
        'Caucasian Shepherd Dog': 'https://www.pets4homes.co.uk/sale/puppies/caucasian-shepherd-dog/',
        'Cava Tzu': 'https://www.pets4homes.co.uk/sale/puppies/cava-tzu/',
        'Cavachon': 'https://www.pets4homes.co.uk/sale/puppies/cavachon/',
        'Cavalier King Charles Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/cavalier-king-charles-spaniel/',
        'Cavapoo': 'https://www.pets4homes.co.uk/sale/puppies/cavapoo/',
        'Cavapoochon': 'https://www.pets4homes.co.uk/sale/puppies/cavapoochon/',
        'Central Asian Shepherd': 'https://www.pets4homes.co.uk/sale/puppies/central-asian-shepherd/',
        'Cesky Terrier': 'https://www.pets4homes.co.uk/sale/puppies/cesky-terrier/',
        'Chesapeake Bay Retriever': 'https://www.pets4homes.co.uk/sale/puppies/chesapeake-bay-retriever/',
        'Chihuahua': 'https://www.pets4homes.co.uk/sale/puppies/chihuahua/',
        'Chinese Crested': 'https://www.pets4homes.co.uk/sale/puppies/chinese-crested/',
        'Chinese Red Dog': 'https://www.pets4homes.co.uk/sale/puppies/chinese-red-dog/',
        'Chipoo': 'https://www.pets4homes.co.uk/sale/puppies/chipoo/',
        'Chiweenie': 'https://www.pets4homes.co.uk/sale/puppies/chiweenie/',
        'Chorkie': 'https://www.pets4homes.co.uk/sale/puppies/chorkie/',
        'Chow Chow': 'https://www.pets4homes.co.uk/sale/puppies/chow-chow/',
        'Chug': 'https://www.pets4homes.co.uk/sale/puppies/chug/',
        'Cirneco DellEtna': 'https://www.pets4homes.co.uk/sale/puppies/cirneco-delletna/',
        'Clumber Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/clumber-spaniel/',
        'Cockalier': 'https://www.pets4homes.co.uk/sale/puppies/cockalier/',
        'Cockapoo': 'https://www.pets4homes.co.uk/sale/puppies/cockapoo/',
        'Cocker Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/cocker-spaniel/',
        'Cockerdor': 'https://www.pets4homes.co.uk/sale/puppies/cockerdor/',
        'Rough Collie': 'https://www.pets4homes.co.uk/sale/puppies/rough-collie/',
        'Smooth Collie': 'https://www.pets4homes.co.uk/sale/puppies/smooth-collie/',
        'Coonhound': 'https://www.pets4homes.co.uk/sale/puppies/coonhound/',
        'Coton de Tulear': 'https://www.pets4homes.co.uk/sale/puppies/coton-de-tulear/',
        'Curly Coated Retriever': 'https://www.pets4homes.co.uk/sale/puppies/curly-coated-retriever/',
        'Dachshund': 'https://www.pets4homes.co.uk/sale/puppies/dachshund/',
        'Miniature Dachshund': 'https://www.pets4homes.co.uk/sale/puppies/miniature-dachshund/',
        'Dalmatian': 'https://www.pets4homes.co.uk/sale/puppies/dalmatian/',
        'Dandie Dinmont Terrier': 'https://www.pets4homes.co.uk/sale/puppies/dandie-dinmont-terrier/',
        'Deerhound': 'https://www.pets4homes.co.uk/sale/puppies/deerhound/',
        'Dobermann': 'https://www.pets4homes.co.uk/sale/puppies/dobermann/',
        'Dogue de Bordeaux': 'https://www.pets4homes.co.uk/sale/puppies/dogue-de-bordeaux/',
        'Dorset Olde Tyme Bulldogge': 'https://www.pets4homes.co.uk/sale/puppies/dorset-olde-tyme-bulldogge/',
        'Double Doodle': 'https://www.pets4homes.co.uk/sale/puppies/double-doodle/',
        'Doxiepoo': 'https://www.pets4homes.co.uk/sale/puppies/doxiepoo/',
        'Foxhound': 'https://www.pets4homes.co.uk/sale/puppies/foxhound/',
        'English Setter': 'https://www.pets4homes.co.uk/sale/puppies/english-setter/',
        'English Springer Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/english-springer-spaniel/',
        'English Toy Terrier': 'https://www.pets4homes.co.uk/sale/puppies/english-toy-terrier/',
        'Entlebucher Mountain Dog': 'https://www.pets4homes.co.uk/sale/puppies/entlebucher-mountain-dog/',
        'Estrela Mountain Dog': 'https://www.pets4homes.co.uk/sale/puppies/estrela-mountain-dog/',
        'Eurasier': 'https://www.pets4homes.co.uk/sale/puppies/eurasier/',
        'Field Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/field-spaniel/',
        'Finnish Lapphund': 'https://www.pets4homes.co.uk/sale/puppies/finnish-lapphund/',
        'Finnish Spitz': 'https://www.pets4homes.co.uk/sale/puppies/finnish-spitz/',
        'Flat Coated Retriever': 'https://www.pets4homes.co.uk/sale/puppies/flat-coated-retriever/',
        'Fox Terrier': 'https://www.pets4homes.co.uk/sale/puppies/fox-terrier/',
        'French Bulldog': 'https://www.pets4homes.co.uk/sale/puppies/french-bulldog/',
        'Frug': 'https://www.pets4homes.co.uk/sale/puppies/frug/',
        'Jagdterrier': 'https://www.pets4homes.co.uk/sale/puppies/jagdterrier/',
        'German Longhaired Pointer': 'https://www.pets4homes.co.uk/sale/puppies/german-longhaired-pointer/',
        'German Pinscher': 'https://www.pets4homes.co.uk/sale/puppies/german-pinscher/',
        'German Shepherd': 'https://www.pets4homes.co.uk/sale/puppies/german-shepherd/',
        'German Shorthaired Pointer': 'https://www.pets4homes.co.uk/sale/puppies/german-shorthaired-pointer/',
        'German Spitz': 'https://www.pets4homes.co.uk/sale/puppies/german-spitz/',
        'German Wirehaired Pointer': 'https://www.pets4homes.co.uk/sale/puppies/german-wirehaired-pointer/',
        'Giant Schnauzer': 'https://www.pets4homes.co.uk/sale/puppies/giant-schnauzer/',
        'Glen of Imaal Terrier': 'https://www.pets4homes.co.uk/sale/puppies/glen-of-imaal-terrier/',
        'Goldador': 'https://www.pets4homes.co.uk/sale/puppies/goldador/',
        'Golden Retriever': 'https://www.pets4homes.co.uk/sale/puppies/golden-retriever/',
        'Golden Shepherd': 'https://www.pets4homes.co.uk/sale/puppies/golden-shepherd/',
        'Goldendoodle': 'https://www.pets4homes.co.uk/sale/puppies/goldendoodle/',
        'Gordon Setter': 'https://www.pets4homes.co.uk/sale/puppies/gordon-setter/',
        'Basset Griffon Vendeen': 'https://www.pets4homes.co.uk/sale/puppies/basset-griffon-vendeen/',
        'Grand Bleu De Gascogne': 'https://www.pets4homes.co.uk/sale/puppies/grand-bleu-de-gascogne/',
        'Great Dane': 'https://www.pets4homes.co.uk/sale/puppies/great-dane/',
        'Greater Swiss Mountain Dog': 'https://www.pets4homes.co.uk/sale/puppies/greater-swiss-mountain-dog/',
        'Greenland Dog': 'https://www.pets4homes.co.uk/sale/puppies/greenland-dog/',
        'Greyhound': 'https://www.pets4homes.co.uk/sale/puppies/greyhound/',
        'Griffon Bruxellois': 'https://www.pets4homes.co.uk/sale/puppies/griffon-bruxellois/',
        'Hamiltonstovare': 'https://www.pets4homes.co.uk/sale/puppies/hamiltonstovare/',
        'Harrier': 'https://www.pets4homes.co.uk/sale/puppies/harrier/',
        'Havanese': 'https://www.pets4homes.co.uk/sale/puppies/havanese/',
        'Havapoo': 'https://www.pets4homes.co.uk/sale/puppies/havapoo/',
        'Hovawart': 'https://www.pets4homes.co.uk/sale/puppies/hovawart/',
        'Huskita': 'https://www.pets4homes.co.uk/sale/puppies/huskita/',
        'Ibizan Hound': 'https://www.pets4homes.co.uk/sale/puppies/ibizan-hound/',
        'Irish Doodle': 'https://www.pets4homes.co.uk/sale/puppies/irish-doodle/',
        'Irish Setter': 'https://www.pets4homes.co.uk/sale/puppies/irish-setter/',
        'Irish Terrier': 'https://www.pets4homes.co.uk/sale/puppies/irish-terrier/',
        'Irish Water Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/irish-water-spaniel/',
        'Irish Wolfhound': 'https://www.pets4homes.co.uk/sale/puppies/irish-wolfhound/',
        'Italian Greyhound': 'https://www.pets4homes.co.uk/sale/puppies/italian-greyhound/',
        'Jack Chi': 'https://www.pets4homes.co.uk/sale/puppies/jack-chi/',
        'Jack Russell': 'https://www.pets4homes.co.uk/sale/puppies/jack-russell/',
        'Jackapoo': 'https://www.pets4homes.co.uk/sale/puppies/jackapoo/',
        'Jackshund': 'https://www.pets4homes.co.uk/sale/puppies/jackshund/',
        'Japanese Chin': 'https://www.pets4homes.co.uk/sale/puppies/japanese-chin/',
        'Japanese Spitz': 'https://www.pets4homes.co.uk/sale/puppies/japanese-spitz/',
        'Jug': 'https://www.pets4homes.co.uk/sale/puppies/jug/',
        'Turkish Kangal': 'https://www.pets4homes.co.uk/sale/puppies/turkish-kangal/',
        'Keeshond': 'https://www.pets4homes.co.uk/sale/puppies/keeshond/',
        'Kerry Blue Terrier': 'https://www.pets4homes.co.uk/sale/puppies/kerry-blue-terrier/',
        'King Charles Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/king-charles-spaniel/',
        'Kishu dog': 'https://www.pets4homes.co.uk/sale/puppies/kishu-dog/',
        'Komondor': 'https://www.pets4homes.co.uk/sale/puppies/komondor/',
        'Kooikerhondje': 'https://www.pets4homes.co.uk/sale/puppies/kooikerhondje/',
        'Korean Jindo': 'https://www.pets4homes.co.uk/sale/puppies/korean-jindo/',
        'Kromfohrlander': 'https://www.pets4homes.co.uk/sale/puppies/kromfohrlander/',
        'Hungarian Kuvasz': 'https://www.pets4homes.co.uk/sale/puppies/hungarian-kuvasz/',
        'Labradoodle': 'https://www.pets4homes.co.uk/sale/puppies/labradoodle/',
        'Labrador Retriever': 'https://www.pets4homes.co.uk/sale/puppies/labrador-retriever/',
        'Lagotto Romagnolo': 'https://www.pets4homes.co.uk/sale/puppies/lagotto-romagnolo/',
        'Lakeland Terrier': 'https://www.pets4homes.co.uk/sale/puppies/lakeland-terrier/',
        'Lancashire Heeler': 'https://www.pets4homes.co.uk/sale/puppies/lancashire-heeler/',
        'Large Munsterlander': 'https://www.pets4homes.co.uk/sale/puppies/large-munsterlander/',
        'Leonberger': 'https://www.pets4homes.co.uk/sale/puppies/leonberger/',
        'Lhasa Apso': 'https://www.pets4homes.co.uk/sale/puppies/lhasa-apso/',
        'Lhasapoo': 'https://www.pets4homes.co.uk/sale/puppies/lhasapoo/',
        'Lowchen': 'https://www.pets4homes.co.uk/sale/puppies/lowchen/',
        'Lurcher': 'https://www.pets4homes.co.uk/sale/puppies/lurcher/',
        'Malshi': 'https://www.pets4homes.co.uk/sale/puppies/malshi/',
        'Maltese': 'https://www.pets4homes.co.uk/sale/puppies/maltese/',
        'Maltipom': 'https://www.pets4homes.co.uk/sale/puppies/maltipom/',
        'Maltipoo': 'https://www.pets4homes.co.uk/sale/puppies/maltipoo/',
        'Manchester Terrier': 'https://www.pets4homes.co.uk/sale/puppies/manchester-terrier/',
        'Maremma Sheepdog': 'https://www.pets4homes.co.uk/sale/puppies/maremma-sheepdog/',
        'Mastiff': 'https://www.pets4homes.co.uk/sale/puppies/mastiff/',
        'Mi-Ki': 'https://www.pets4homes.co.uk/sale/puppies/mi-ki/',
        'Mini Goldendoodle': 'https://www.pets4homes.co.uk/sale/puppies/mini-goldendoodle/',
        'Miniature American Shepherd': 'https://www.pets4homes.co.uk/sale/puppies/miniature-american-shepherd/',
        'Miniature Pinscher': 'https://www.pets4homes.co.uk/sale/puppies/miniature-pinscher/',
        'Miniature Schnauzer': 'https://www.pets4homes.co.uk/sale/puppies/miniature-schnauzer/',
        'Mixed Breed': 'https://www.pets4homes.co.uk/sale/puppies/mixed-breed/',
        'Morkie': 'https://www.pets4homes.co.uk/sale/puppies/morkie/',
        'Neapolitan Mastiff': 'https://www.pets4homes.co.uk/sale/puppies/neapolitan-mastiff/',
        'Huntaway': 'https://www.pets4homes.co.uk/sale/puppies/huntaway/',
        'Newfoundland': 'https://www.pets4homes.co.uk/sale/puppies/newfoundland/',
        'Newfypoo': 'https://www.pets4homes.co.uk/sale/puppies/newfypoo/',
        'Norfolk Terrier': 'https://www.pets4homes.co.uk/sale/puppies/norfolk-terrier/',
        'Northern Inuit': 'https://www.pets4homes.co.uk/sale/puppies/northern-inuit/',
        'Norwegian Buhund': 'https://www.pets4homes.co.uk/sale/puppies/norwegian-buhund/',
        'Norwegian Elkhound': 'https://www.pets4homes.co.uk/sale/puppies/norwegian-elkhound/',
        'Norwich Terrier': 'https://www.pets4homes.co.uk/sale/puppies/norwich-terrier/',
        'Nova Scotia Duck Tolling Retriever': 'https://www.pets4homes.co.uk/sale/puppies/nova-scotia-duck-tolling-retriever/',
        'Old English Sheepdog': 'https://www.pets4homes.co.uk/sale/puppies/old-english-sheepdog/',
        'Old Tyme Bulldog': 'https://www.pets4homes.co.uk/sale/puppies/old-tyme-bulldog/',
        'Olde English Bulldogge': 'https://www.pets4homes.co.uk/sale/puppies/olde-english-bulldogge/',
        'Otterhound': 'https://www.pets4homes.co.uk/sale/puppies/otterhound/',
        'Papillon': 'https://www.pets4homes.co.uk/sale/puppies/papillon/',
        'Parson Russell': 'https://www.pets4homes.co.uk/sale/puppies/parson-russell/',
        'Patterdale Terrier': 'https://www.pets4homes.co.uk/sale/puppies/patterdale-terrier/',
        'Patterjack': 'https://www.pets4homes.co.uk/sale/puppies/patterjack/',
        'Pekingese': 'https://www.pets4homes.co.uk/sale/puppies/pekingese/',
        'Welsh Corgi Pembroke': 'https://www.pets4homes.co.uk/sale/puppies/welsh-corgi-pembroke/',
        'Pharaoh Hound': 'https://www.pets4homes.co.uk/sale/puppies/pharaoh-hound/',
        'Picardy Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/picardy-spaniel/',
        'Plummer Terrier': 'https://www.pets4homes.co.uk/sale/puppies/plummer-terrier/',
        'Pointer': 'https://www.pets4homes.co.uk/sale/puppies/pointer/',
        'Polish Lowland Sheepdog': 'https://www.pets4homes.co.uk/sale/puppies/polish-lowland-sheepdog/',
        'Pomapoo': 'https://www.pets4homes.co.uk/sale/puppies/pomapoo/',
        'Pomchi': 'https://www.pets4homes.co.uk/sale/puppies/pomchi/',
        'Pomeranian': 'https://www.pets4homes.co.uk/sale/puppies/pomeranian/',
        'Pomsky': 'https://www.pets4homes.co.uk/sale/puppies/pomsky/',
        'Poochon': 'https://www.pets4homes.co.uk/sale/puppies/poochon/',
        'Poodle': 'https://www.pets4homes.co.uk/sale/puppies/poodle/',
        'Miniature Poodle': 'https://www.pets4homes.co.uk/sale/puppies/miniature-poodle/',
        'Standard Poodle': 'https://www.pets4homes.co.uk/sale/puppies/standard-poodle/',
        'Toy Poodle': 'https://www.pets4homes.co.uk/sale/puppies/toy-poodle/',
        'Portuguese Podengo': 'https://www.pets4homes.co.uk/sale/puppies/portuguese-podengo/',
        'Portuguese Sheepdog': 'https://www.pets4homes.co.uk/sale/puppies/portuguese-sheepdog/',
        'Portuguese Water Dog': 'https://www.pets4homes.co.uk/sale/puppies/portuguese-water-dog/',
        'Presa Canario': 'https://www.pets4homes.co.uk/sale/puppies/presa-canario/',
        'Pug': 'https://www.pets4homes.co.uk/sale/puppies/pug/',
        'Pugapoo': 'https://www.pets4homes.co.uk/sale/puppies/pugapoo/',
        'Puggle': 'https://www.pets4homes.co.uk/sale/puppies/puggle/',
        'Hungarian Puli': 'https://www.pets4homes.co.uk/sale/puppies/hungarian-puli/',
        'Hungarian Pumi': 'https://www.pets4homes.co.uk/sale/puppies/hungarian-pumi/',
        'Pyrenean Mastiff': 'https://www.pets4homes.co.uk/sale/puppies/pyrenean-mastiff/',
        'Pyrenean Mountain Dog': 'https://www.pets4homes.co.uk/sale/puppies/pyrenean-mountain-dog/',
        'Pyrenean Sheepdog': 'https://www.pets4homes.co.uk/sale/puppies/pyrenean-sheepdog/',
        'Rhodesian Ridgeback': 'https://www.pets4homes.co.uk/sale/puppies/rhodesian-ridgeback/',
        'Rottweiler': 'https://www.pets4homes.co.uk/sale/puppies/rottweiler/',
        'Russian Toy Terrier': 'https://www.pets4homes.co.uk/sale/puppies/russian-toy-terrier/',
        'Saarloos Wolfdog': 'https://www.pets4homes.co.uk/sale/puppies/saarloos-wolfdog/',
        'Saluki': 'https://www.pets4homes.co.uk/sale/puppies/saluki/',
        'Samoyed': 'https://www.pets4homes.co.uk/sale/puppies/samoyed/',
        'Schipperke': 'https://www.pets4homes.co.uk/sale/puppies/schipperke/',
        'Schnoodle': 'https://www.pets4homes.co.uk/sale/puppies/schnoodle/',
        'Scottish Terrier': 'https://www.pets4homes.co.uk/sale/puppies/scottish-terrier/',
        'Sealyham Terrier': 'https://www.pets4homes.co.uk/sale/puppies/sealyham-terrier/',
        'Segugio Italiano': 'https://www.pets4homes.co.uk/sale/puppies/segugio-italiano/',
        'Shar Pei': 'https://www.pets4homes.co.uk/sale/puppies/shar-pei/',
        'Sheepadoodle': 'https://www.pets4homes.co.uk/sale/puppies/sheepadoodle/',
        'Sheprador': 'https://www.pets4homes.co.uk/sale/puppies/sheprador/',
        'Shepsky': 'https://www.pets4homes.co.uk/sale/puppies/shepsky/',
        'Shetland Sheepdog': 'https://www.pets4homes.co.uk/sale/puppies/shetland-sheepdog/',
        'Japanese Shiba Inu': 'https://www.pets4homes.co.uk/sale/puppies/japanese-shiba-inu/',
        'Shichon': 'https://www.pets4homes.co.uk/sale/puppies/shichon/',
        'Shih Tzu': 'https://www.pets4homes.co.uk/sale/puppies/shih-tzu/',
        'Shihpoo': 'https://www.pets4homes.co.uk/sale/puppies/shihpoo/',
        'Shorkie': 'https://www.pets4homes.co.uk/sale/puppies/shorkie/',
        'Shorty Bull': 'https://www.pets4homes.co.uk/sale/puppies/shorty-bull/',
        'Siberian Husky': 'https://www.pets4homes.co.uk/sale/puppies/siberian-husky/',
        'Skye Terrier': 'https://www.pets4homes.co.uk/sale/puppies/skye-terrier/',
        'Sloughi': 'https://www.pets4homes.co.uk/sale/puppies/sloughi/',
        'Soft Coated Wheaten Terrier': 'https://www.pets4homes.co.uk/sale/puppies/soft-coated-wheaten-terrier/',
        'Spanish Water Dog': 'https://www.pets4homes.co.uk/sale/puppies/spanish-water-dog/',
        'Italian Spinone': 'https://www.pets4homes.co.uk/sale/puppies/italian-spinone/',
        'Sporting Lucas Terrier': 'https://www.pets4homes.co.uk/sale/puppies/sporting-lucas-terrier/',
        'Springador': 'https://www.pets4homes.co.uk/sale/puppies/springador/',
        'Sprocker': 'https://www.pets4homes.co.uk/sale/puppies/sprocker/',
        'Sprollie': 'https://www.pets4homes.co.uk/sale/puppies/sprollie/',
        'Sproodle': 'https://www.pets4homes.co.uk/sale/puppies/sproodle/',
        'Saint Bernard': 'https://www.pets4homes.co.uk/sale/puppies/saint-bernard/',
        'Stabyhoun': 'https://www.pets4homes.co.uk/sale/puppies/stabyhoun/',
        'Staffordshire Bull Terrier': 'https://www.pets4homes.co.uk/sale/puppies/staffordshire-bull-terrier/',
        'Schnauzer': 'https://www.pets4homes.co.uk/sale/puppies/schnauzer/',
        'Sussex Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/sussex-spaniel/',
        'Swedish Lapphund': 'https://www.pets4homes.co.uk/sale/puppies/swedish-lapphund/',
        'Swedish Vallhund': 'https://www.pets4homes.co.uk/sale/puppies/swedish-vallhund/',
        'Thai Ridgeback': 'https://www.pets4homes.co.uk/sale/puppies/thai-ridgeback/',
        'Tibetan Mastiff': 'https://www.pets4homes.co.uk/sale/puppies/tibetan-mastiff/',
        'Tibetan Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/tibetan-spaniel/',
        'Tibetan Terrier': 'https://www.pets4homes.co.uk/sale/puppies/tibetan-terrier/',
        'Utonagan': 'https://www.pets4homes.co.uk/sale/puppies/utonagan/',
        'Hungarian Vizsla': 'https://www.pets4homes.co.uk/sale/puppies/hungarian-vizsla/',
        'Weimaraner': 'https://www.pets4homes.co.uk/sale/puppies/weimaraner/',
        'Welsh Collie': 'https://www.pets4homes.co.uk/sale/puppies/welsh-collie/',
        'Welsh Springer Spaniel': 'https://www.pets4homes.co.uk/sale/puppies/welsh-springer-spaniel/',
        'Welsh Terrier': 'https://www.pets4homes.co.uk/sale/puppies/welsh-terrier/',
        'West Highland Terrier': 'https://www.pets4homes.co.uk/sale/puppies/west-highland-terrier/',
        'Westiepoo': 'https://www.pets4homes.co.uk/sale/puppies/westiepoo/',
        'Whippet': 'https://www.pets4homes.co.uk/sale/puppies/whippet/',
        'White Swiss Shepherd': 'https://www.pets4homes.co.uk/sale/puppies/white-swiss-shepherd/',
        'Korthals Griffon': 'https://www.pets4homes.co.uk/sale/puppies/korthals-griffon/',
        'Mexican Hairless': 'https://www.pets4homes.co.uk/sale/puppies/mexican-hairless/',
        'Yorkiepoo': 'https://www.pets4homes.co.uk/sale/puppies/yorkiepoo/',
        'Yorkshire Terrier': 'https://www.pets4homes.co.uk/sale/puppies/yorkshire-terrier/',
        'Yochon': 'https://www.pets4homes.co.uk/sale/puppies/yochon/',
        'Zuchon': 'https://www.pets4homes.co.uk/sale/puppies/zuchon/',
    }
    
    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    FIELDNAMES = ['title', 'breed', 'date_of_birth', 'males_available', 'females_available', 
        'total_available', 'price', 'description', 'sellerBadges', 'location', 'ready_to_leave',
        'url', 'created_at', 'published_at', 'refreshed_at', 'views_count', 'seller_id', 'seller_name', 'company_name', 'user_type', 'is_breeder',
        'active_listings', 'active_pets', 'member_since', 'last_active', 'response_hours',
        'license_num', 'license_auth', 'license_status', 'license_valid',
        'kc_license', 'email_verified', 'phone_verified', 'reviews', 'rating']
    
    def __init__(self):
        self.seen_urls = set()
        self.results = []
        self.output_file = os.path.join(os.getcwd(), 'pets4homes_v7_complete.csv')
        print(f"Output: {self.output_file}")
        
    def _request(self, url, retries=3):
        for attempt in range(retries):
            try:
                time.sleep(random.uniform(1.5, 3))
                r = requests.get(url, headers=self.HEADERS, timeout=30)
                if r.status_code == 200: return r
                if r.status_code == 429: time.sleep(30)
            except:
                if attempt < retries - 1: time.sleep(5)
        return None
    
    def _get_attr(self, attrs, key):
        for a in attrs:
            if a.get('key') == key:
                return a.get('value', '')
        return ''
    
    def _camel_to_readable(self, name):
        if not name: return ''
        result = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return result.title()
    
    def _unix_ms_to_date(self, unix_ms):
        if not unix_ms: return ''
        try:
            return datetime.fromtimestamp(int(unix_ms)/1000).strftime('%Y-%m-%d')
        except:
            return str(unix_ms)
    
    def _clean_string(self, val):
        if val is None: return ''
        s = str(val).strip()
        if s.lower() in ('nan', 'none', ''): return ''
        return s
    
    def _extract(self, url):
        r = self._request(url)
        if not r: return None
        try:
            soup = BeautifulSoup(r.content, 'html.parser')
            tag = soup.find('script', id='__NEXT_DATA__')
            if not tag: return None
            listing = json.loads(tag.string).get('props',{}).get('pageProps',{}).get('listing',{})
            if not listing: return None
            
            gen_info = listing.get('generalInformation', {})
            attrs = listing.get('attributes', [])
            
            breed_raw = self._get_attr(attrs, 'breed')
            breed = self._camel_to_readable(breed_raw.split('.')[-1]) if breed_raw else ''
            
            price_obj = gen_info.get('price', {})
            price_val = price_obj.get('amount', '') if price_obj else ''
            price = f"£{price_val}" if price_val else ''
            
            males = self._get_attr(attrs, 'numberOfMales')
            females = self._get_attr(attrs, 'numberOfFemales')
            
            total_available = ''
            try:
                if males or females:
                    total_available = str((int(males) if males else 0) + (int(females) if females else 0))
            except: pass
            
            dob_raw = self._get_attr(attrs, 'dateOfBirth')
            
            data = {
                'title': gen_info.get('title', ''),
                'breed': breed,
                'date_of_birth': self._unix_ms_to_date(dob_raw),
                'males_available': males,
                'females_available': females,
                'total_available': total_available,
                'price': price,
                'description': gen_info.get('description', ''),
                'ready_to_leave': self._get_attr(attrs, 'readyToLeave'),
                'url': url,
                'created_at': listing.get('created_at', '').split('T')[0] if listing.get('created_at') else '',
                'published_at': listing.get('publishedAt', '').split('T')[0] if listing.get('publishedAt') else '',
                'refreshed_at': listing.get('refreshedAt', '').split('T')[0] if listing.get('refreshedAt') else '',
                'views_count': listing.get('viewsCount', ''),
            }
            
            loc = listing.get('locationV3', {})
            if loc:
                town = loc.get('postalTown', '')
                county = loc.get('adminRegion2', '')
                data['location'] = f"{town}, {county}" if town and county else (town or county)
            else:
                data['location'] = ''
            
            badges = []
            if listing.get('user', {}).get('license'): badges.append('Licensed Breeder')
            if listing.get('isUserIdentityVerified'): badges.append('ID Verified')
            data['sellerBadges'] = ', '.join(badges)
            
            u = listing.get('user', {})
            if u:
                g = u.get('generalInformations', {})
                l = u.get('license', {})
                k = u.get('kcLicense', {})
                v = u.get('verifications', {})
                t = g.get('userType', {})
                
                seller_name = self._clean_string(g.get('profileName'))
                if not seller_name:
                    first = self._clean_string(g.get('firstName'))
                    last = self._clean_string(g.get('lastName'))
                    seller_name = f"{first} {last}".strip()
                
                data.update({
                    'seller_id': u.get('id', ''),
                    'seller_name': seller_name,
                    'company_name': self._clean_string(g.get('companyName')) or self._clean_string(g.get('charityName')),
                    'user_type': t.get('type', '') if isinstance(t, dict) else t,
                    'is_breeder': u.get('isFullServiceBreeder', ''),
                    'active_listings': u.get('activeListingsCount', ''),
                    'active_pets': u.get('activePetsCount', ''),
                    'member_since': u.get('createdAt', '').split('T')[0] if u.get('createdAt') else '',
                    'last_active': u.get('lastActive', '').split('T')[0] if u.get('lastActive') else '',
                    'response_hours': round(u.get('averageResponseTime', 0)/3600, 1) if u.get('averageResponseTime') else '',
                    'license_num': l.get('number', '') if l else '',
                    'license_auth': l.get('authorityName', '') if l else '',
                    'license_status': l.get('status', '') if l else '',
                    'license_valid': l.get('isValid', '') if l else '',
                    'kc_license': k.get('number', '') if k else '',
                    'email_verified': v.get('email', '') if v else '',
                    'phone_verified': v.get('phoneNumber', '') if v else '',
                    'reviews': u.get('sellerReviewsCount', ''),
                    'rating': u.get('sellerReviewsAverageRating', '')
                })
            return data
        except: return None
    
    def _collect_urls(self, breed_url, max_pages=100):
        for page in range(1, max_pages + 1):
            url = breed_url if page == 1 else f"{breed_url}?page={page}"
            r = self._request(url)
            if not r: break
            soup = BeautifulSoup(r.content, 'html.parser')
            new = 0
            for link in soup.find_all('a', href=lambda x: x and '/classifieds/' in x):
                if not link.find('h3'): continue
                href = link.get('href', '')
                if '/classifieds/' in href:
                    full = f"https://www.pets4homes.co.uk{href}" if href.startswith('/') else href
                    if full not in self.seen_urls:
                        self.seen_urls.add(full)
                        new += 1
            if new > 0: print(f"    Page {page}: +{new} (total: {len(self.seen_urls)})")
            if new == 0: break
    
    def _save(self):
        if not self.results: return False
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                csv.DictWriter(f, fieldnames=self.FIELDNAMES).writeheader()
                csv.DictWriter(f, fieldnames=self.FIELDNAMES).writerows(self.results)
            print(f"SAVED: {os.path.getsize(self.output_file):,} bytes, {len(self.results)} rows")
            return True
        except Exception as e:
            print(f"ERROR: {e}")
            return False
    
    def scrape(self):
        start = datetime.now()
        print("="*60)
        print("Pets4Homes Scraper v7 - ULTIMATE EDITION")
        print(f"Started: {start.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        print("\nPHASE 1: Collecting URLs")
        for i, (name, url) in enumerate(self.BREED_URLS.items(), 1):
            print(f"[{i}/{len(self.BREED_URLS)}] {name}...")
            self._collect_urls(url)
        print(f"\n{len(self.seen_urls)} unique URLs\n")
        
        print("PHASE 2: Scraping listings")
        for i, url in enumerate(list(self.seen_urls), 1):
            print(f"[{i}/{len(self.seen_urls)} {i*100//len(self.seen_urls)}%] {url.split('/')[-2][:35]}...", end=' ')
            data = self._extract(url)
            if data:
                self.results.append(data)
                print(f"OK {data.get('price', '?')}")
            else: print("FAIL")
            if i % 100 == 0:
                self._save()
                elapsed = (datetime.now()-start).total_seconds()
                eta = (len(self.seen_urls)-i) / (i/elapsed) / 60 if elapsed > 0 else 0
                print(f"\n>>> {len(self.results)} saved | ETA: {eta:.0f}min\n")
        
        print("\n" + "="*60)
        self._save()
        print(f"DONE! {len(self.results)} listings in {datetime.now()-start}")
        print("="*60)

if __name__ == '__main__':
    Pets4HomesScraper().scrape()
