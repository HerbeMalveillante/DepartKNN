"""
Ce programme permet de deviner le département d'un point GPS quelconque.
Il utilise un algorithme des k plus proches voisins
Utilise les données du site data.gouv

V1 : Fichier élève
"""
import folium
from math import sin, cos, acos, radians, sqrt
#from editeCarte_V1_1 import creerCarte






def creerCarte(lstVilles,posGPS,dicoKNN,distKNN) :
    """
    lstVilles est la liste des villes de france telle qu'elle est renvoyée par creerLstVilles,
    chaque élément est au format [47.116667, 5.883333, 'Abbans-Dessus', '25'].
    
    posGPS est un tuple contenant les coordonées du point recherché.
    
    dicoKNN est le dictionnaire fourni par la fonction KNN au format
    {'numDepart' : [indexCommune1, indexCommune2, indexCommune3], 'numDepart2' : [indexCommune4, indexCommune5, indexCommune6]
    qui contient toutes les communes dans le rayon spécifié triées par département
    
    distKNN est le rayon de recherche.
    """
    
    plusGrandsDepartements = maxDic(dicoKNN)
    m = folium.Map(location=list(posGPS))
    
    #les départements en vert sont les départements compris dans plusGrandsDepartements
    dptG = plusGrandsDepartements
    
    #les départements en rouge sont les départements qui sont des clefs dans dicoKNN SAUF celles présentes dans dptG.
    dptR = []
    for depart in dicoKNN.keys():
        if depart not in dptG :
            dptR.append(depart)
            
    print(dptR)
    print(dptG)
    
    
    #ajout des départements
    folium.GeoJson(
        'departements.geojson',
        style_function = lambda x: {'weight':1, 'color': '#0000FF', 'fillColor': '#FF0000' if x['properties']['code'] in dptR else ('#00FF00' if x['properties']['code'] in dptG else '#000000')}
        ).add_to(m)


    #ajout du point gps
    folium.Marker(
        location=list(posGPS),
        popup=f"{list(posGPS)}\nDépartement probable : {plusGrandsDepartements}",
        icon=folium.Icon(color="red")).add_to(m)
    
    
    #ajout des cercles pour les communes
    for depart in dicoKNN :
        for index in dicoKNN[depart] :
            
            index = int(index)
            
            if str(lstVilles[index][3]) in plusGrandsDepartements:
                color = "#00FF22"
            else :
                color = "#FF0000"
            
            folium.Circle(
                radius = 500,
                opacity = 0,
                location = [lstVilles[index][0], lstVilles[index][1]],
                popup = f"{lstVilles[index][2]}\n{lstVilles[index][3]}",
                color = color,
                fill_opacity = 0.8,
                fill=True).add_to(m)
                
            

    #ajout du cercle de rayon de recherche
    folium.Circle(
        radius=distKNN*1000,
        location=list(posGPS),
        popup=f"{distKNN}km",
        color='crimson',
        fill=False).add_to(m)
    
    
    m.save('nouvelleCarteKNN.html')
    print("la nouvelle carte a été sauvegardée sous le nom 'nouvelleCarteKNN.html'")
    



#####################################################################
##      Fonctions d'extraction et de mise en forme du CSV          ##
#####################################################################

def creerListeCSV(filename):
    """
    Fonction qui créé une liste à partir d'une table csv.
    Le séparateur est modifiable.
    """
    f = open(filename, 'r', encoding = "utf-8")
    table = [] #une liste vide pour recevoir la table
    
    while True: #tant qu'il reste des lignes a lire
        ligne = f.readline() #lit une ligne

        if ligne != "":
            lstLigne = ligne.split(';')
            table.append(lstLigne)
        else:
            #le fichier est parcouru entièrement
            f.close()
            return table[1:]
        
def creerLstVilles (liste):
    """
    Supprime les colonnes inutiles
    Transforme en flottant les coordonnées GPS.
    créé une nouvelle liste et la renvoi
    Avec le descripteur suivant :
    [latitude (float), longitude (float), nom de la commune (str), numéro département (str)]
    liste est la liste de toutes les communes de France, elle n'est pas modifiée par cette fonction
    """
    nouvelle_liste = []
    failed = 0
    for commune in liste :
        
        latitude = commune[11]
        longitude = commune[12]
        nom = commune[8]
        numdepart = commune[4]

        try :
            nouvelle_liste.append([float(latitude), float(longitude), str(nom), str(numdepart)])
        except :
            #print(f"la commune {commune[8]} n'a pas été ajouté à la liste car ses coordonnées ne sont pas présentes dans la base de donnée.")
            failed += 1
    #print(f"fin du formatage. Nombre de communes dont les coordonnées ne sont pas accessibles : {failed}")
    #print(f"Nombre de communes dont les coordonnées sont accessibles : {len(liste)-failed}")
    return nouvelle_liste        

def creerDicoDep(liste):
    """
    Crée et renvoi un dictionnaire qui associe les numéros de département (clé en str)
    au nom des départements (valeur, également en str)
    liste est la liste de toutes les communes de France, elle n'est pas modifiée par cette fonction
    
    """
    dico = {}
    for i in liste :
        if i[4] not in dico :
            dico[str(i[4])] = str(i[5])
    return dico
    
    

#####################################################################
##                 Fonctions pour Algorithme des K-NN              ##
#####################################################################

def longueurSurTerre(pos1, pos2):
    """
    Renvoi la distance en km sur la surface du globe
    entre deux points de coordonnées GPS pos1 et pos2
    pos1 et pos2 sont des tupples de la forme (latitude, longitude)
    version très approchée : raisonnable sur de courtes distances
    
    la distance entre Alençon et Toulouse mesurée avec Google Maps est 546,04km. Celle mesurée avec le programme est de 555.27km.
    la distance entre Poitiers et Besançon mesurée avec Google Maps est 439,23km. Celle mesurée avec le programme est de 635.61km.
    Il est intéressant de noter que la mesure est plutôt précise pour la distance Alençon-Toulouse, mais que la mesure Poitiers-Besançons l'est beaucoup moins malgré une distance effective moins grande. J'ai déjà vérifié les coordonnées gps et ma mesure sur Google Maps plusieurs fois.
    
    """
    dLat = radians(pos1[0]-pos2[0])
    dLong = radians(pos1[1]-pos2[1])
    return 6378 * sqrt(dLat**2+dLong**2)

def longueurSurTerre2(pos1,pos2):
    """
    Renvoie la distance en km sur la surface du globe
    entre deux points de coordonnées GPS pos1 et pos2
    pos1 et pos2 sont des tupples de la forme (latitude, longitude)
    version très précise
    
    la distance entre Alençon et Toulouse mesurée avec Google Maps est 546,04km. Celle mesurée avec le programme est de 544.67km.
    la distance entre Poitiers et Besançon mesurée avec Google Maps est 439,23km. Celle mesurée avec le programme est de 437.4km.
    Cette fois ci, les distances sont très précises.
    """
    phia = radians(pos1[0])
    phib = radians(pos2[0])
    lamba = radians(pos1[1])
    lambb = radians(pos2[1])
    
    rad = acos(sin(phia)*sin(phib)+cos(phia)*cos(phib)*cos(lambb-lamba))
    distancem = rad*6378137
    distancekm = distancem / 1000
    return distancekm

def kNN(lstV, pt, distMax):
    """
    lstV est une liste de coordonnée (villes de France par exemple) commençant par (lat, long, ...
    latitude en index 0
    longitude en index 1
    pt est un tupple (latitude, longitude) d'un point particulier
    distMax -> distance de sélection des voisins
    renvoi un dictionnaire qui contient pour clé les numéros de département
    et pour valeur la liste des index des villes voisines de pos
    """

    listeCommunesValides = []
    index = 0
    for commune in lstV :
        distance = longueurSurTerre2((commune[0], commune[1]), pt)
        
        if distance <= distMax :
            listeCommunesValides.append(commune)
            
    dicoRenvoi = {}
    for commune in listeCommunesValides :
        if commune[3] not in dicoRenvoi :
            dicoRenvoi[commune[3]] = [lstV.index(commune)]
        else :
            dicoRenvoi[commune[3]].append(lstV.index(commune))
            
    return dicoRenvoi
    
def maxDic(dic):
    """
    Fontion qui renvoi la ou les clé du dico qui contiennent la plus grande liste
    Cette fonction renvoi une liste de clé.
    """

    #on teste la longueur des listes et on créée une nouvelle liste (plusGrandesListes) qui contient la ou les listes les plus longues.
    listeListes = []
    plusGrandesListes = []
    lenInt = 0
    for list in dic :
        if len(dic[list]) > lenInt :
            plusGrandesListes = []
            plusGrandesListes.append(dic[list])
            lenInt = len(dic[list])

        elif len(dic[list]) == lenInt :
            plusGrandesListes.append(dic[list])
            
    #on doit maintenant chercher dans dictionnaire le ou les index correspondant à la ou les listes retournées et à les mettre dans une liste.
    listeFinal = []
    
    for i in dic :
        if dic[i] in plusGrandesListes :
            listeFinal.append(i)
        
    return listeFinal
                
    

#####################################################################
##             Fonctions Interface homme machine                   ##
#####################################################################

def recommence():
    while True:
        rep = input("Voulez-vous recommencer (o/n) : ")
        if rep in ('o', 'O', 'y', 'Y') :
            return True
        elif rep in ('n', 'N') :
            return False

def saisieGPS (defaut = (48.430673,0.085137)):
    """
    Fonction qui demande a l'utilisateur de saisir une position GPS sous la forme lat, long
    Renvoi un tupple (latitude en float, longitude en float)
    Test si la saisie est conforme aux préconditions suivantes :
    latitude comprise entre -90 et 90°
    longitude comprise entre -180 et 180°
    Dans le cas contraire, la question est reposée jusqu'à obtenir une réponse correcte
    Si l'utilisateur saisi un champ vide, la valeur par défaut est renvoyée
    """    
    while True:
        try:
            rep = input("Indiquez les coordonnées GPS : lat, long ").split(',')
            if rep == [''] :
                print("La saisie est vide, valeur par défaut utilisée.")
                GPS = defaut
            else : 
                GPS = (float(rep[0]), float(rep[1]))
                assert GPS[0] > -90, "La latitude doit être supérieure à -90 !"
                assert GPS[0] < 90, "La latitude doit être inférieure à 90 !"
                assert GPS[1] > -180, "La longitude doit être supérieure à -180 !"
                assert GPS[1] < 180, "La longitude doit être inférieure à 180 !"
            return GPS
        except:
            print("Saisie incorrecte, veuillez recommencer !")


#####################################################################
##                             main                                ##
#####################################################################
def main():
    
    
#    positionVille = (48.430673,0.085137)
    positionVille = saisieGPS() 
    rayonCherche = 10
    
    
    listeCommunes = creerListeCSV('Communes_gps.csv')
    listeVilles = creerLstVilles(listeCommunes)
    dicVilles = kNN(listeVilles, positionVille, rayonCherche)
    plusGrandsDepartements = maxDic(dicVilles)
    
    creerCarte(listeVilles, positionVille , dicVilles, rayonCherche)
    
    
    if recommence():
        main()



#    testAlgo(15,'Communes_gps.csv')
    
    
def testAlgo(rayonCherche, listeCommunes):
    posGPSTest = [(44.367851,0.012273),(48.669160,-0.824551),(48.771205,2.486271),(48.407558,-0.028977),(43.573643,2.711879),(45.794673,6.653018),(48.827363,2.573748)]
    dprtTest = [["47"],["50"],["94"],["61"],["34"],["73"],["93"]]
    
    listeCommunes = creerListeCSV('Communes_gps.csv')
    listeVilles = creerLstVilles(listeCommunes)

    
    print("Début des tests... ")
    for i in range(len(posGPSTest)):
        print(f"Test numéro {i} >>> ", end = "")
        dicVilles = kNN(listeVilles, posGPSTest[i], rayonCherche)
        plusGrandsDepartements = maxDic(dicVilles)
        
        print(f"Le résultat attendu était {dprtTest[i]}, le résultat trouvé est {plusGrandsDepartements}")
    print("fin des tests")
        

    
    

if __name__ == "__main__":
    main()

    
    
    
    
    
    
