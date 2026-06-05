import urllib.request
import json
import os
import re
import time
from datetime import datetime

ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
CF_ACCOUNT_ID = os.environ['CF_ACCOUNT_ID']
CF_KV_NAMESPACE_ID = os.environ['CF_KV_NAMESPACE_ID']
CF_API_TOKEN = os.environ['CF_API_TOKEN']
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')

today = datetime.now().strftime('%A, %B %d, %Y')

# Official FIFA World Cup 2026 squads - all 48 teams
OFFICIAL_SQUADS = {
  "Czech Republic": ["Matěj Kovář","Jindřich Staněk","Lukáš Horníček","Vladimír Coufal","Tomáš Holeš","Ladislav Krejčí","David Zima","Jaroslav Zelený","David Jurásek","David Douděra","Robin Hranáč","Štěpán Chaloupek","Tomáš Souček","Vladimír Darida","Lukáš Provod","Michal Sadílek","Pavel Šulc","Lukáš Červ","Hugo Sochůrek","Alexandr Sojka","Denis Višinský","Patrik Schick","Adam Hložek","Jan Kuchta","Mojmír Chytil","Tomáš Chorý"],
  "Mexico": ["Guillermo Ochoa","Raúl Rangel","Carlos Acevedo","Jesús Gallardo","César Montes","Jorge Sánchez","Johan Vásquez","Israel Reyes","Mateo Chávez","Edson Álvarez","Orbelín Pineda","Roberto Alvarado","Luis Romo","Luis Chávez","Érik Lira","Gilberto Mora","Brian Gutiérrez","Obed Vargas","Álvaro Fidalgo","Raúl Jiménez","Alexis Vega","Santiago Giménez","César Huerta","Julián Quiñones","Guillermo Martínez","Armando González"],
  "South Africa": ["Ronwen Williams","Ricardo Goss","Sipho Chaine","Aubrey Modiba","Khuliso Mudau","Nkosinathi Sibisi","Mbekezeli Mbokazi","Ime Okon","Samukele Kabini","Khulumani Ndamane","Thabang Matuludi","Kamogelo Sebelebele","Bradley Cross","Olwethu Makhanya","Teboho Mokoena","Sphephelo Sithole","Thalente Mbatha","Jayden Adams","Themba Zwane","Lyle Foster","Evidence Makgopa","Oswin Appollis","Iqraam Rayners","Relebohile Mofokeng","Thapelo Maseko","Tshepang Moremi"],
  "South Korea": ["Kim Seung-gyu","Jo Hyeon-woo","Song Bum-keun","Kim Min-jae","Kim Moon-hwan","Seol Young-woo","Lee Tae-seok","Park Jin-seob","Kim Tae-hyeon","Lee Han-beom","Jens Castrop","Lee Ki-hyuk","Cho Wi-je","Lee Jae-sung","Hwang Hee-chan","Hwang In-beom","Lee Kang-in","Paik Seung-ho","Kim Jin-gyu","Lee Dong-gyeong","Bae Jun-ho","Eom Ji-sung","Yang Hyun-jun","Son Heung-min","Cho Gue-sung","Oh Hyeon-gyu"],
  "Bosnia and Herzegovina": ["Nikola Vasilj","Martin Zlomislić","Osman Hadžikić","Sead Kolašinac","Dennis Hadžikadunić","Amar Dedić","Nikola Katić","Tarik Muharemović","Nihad Mujakić","Stjepan Radeljić","Nidal Čelik","Amir Hadžiahmetović","Benjamin Tahirović","Armin Gigović","Dženis Burnić","Ivan Bašić","Esmir Bajraktarević","Amar Memić","Ivan Šunjić","Kerim Alajbegović","Ermin Mahmić","Edin Džeko","Ermedin Demirović","Samed Baždar","Haris Tabaković","Jovo Lukić"],
  "Canada": ["Dayne St. Clair","Maxime Crépeau","Owen Goodman","Alistair Johnston","Luc de Fougerolles","Alfie Jones","Joel Waterman","Derek Cornelius","Moïse Bombito","Alphonso Davies","Richie Laryea","Niko Sigur","Mathieu Choinière","Stephen Eustáquio","Ismaël Koné","Liam Millar","Jacob Shaffelburg","Tajon Buchanan","Ali Ahmed","Jonathan Osorio","Nathan Saliba","Cyle Larin","Jonathan David","Tani Oluwaseyi","Promise David","Marcelo Flores"],
  "Qatar": ["Mahmud Abunada","Salah Zakaria","Meshaal Barsham","Pedro Miguel","Lucas Mendes","Issa Laye","Homam Ahmed","Boualem Khoukhi","Sultan Al-Brake","Al-Hashmi Al-Hussain","Ayoub Al-Oui","Jassem Gaber","Abdulaziz Hatem","Karim Boudiaf","Assim Madibo","Ahmed Fathy","Mohamed Al-Mannai","Ahmed Alaaeldin","Edmilson Junior","Mohammed Muntari","Hassan Al-Haydos","Akram Afif","Yusuf Abdurisag","Ahmed Al-Ganehi","Almoez Ali","Tahsin Jamshid"],
  "Switzerland": ["Gregor Kobel","Yvon Mvogo","Marvin Keller","Miro Muheim","Silvan Widmer","Nico Elvedi","Manuel Akanji","Eray Cömert","Ricardo Rodriguez","Aurèle Amenda","Luca Jaquez","Denis Zakaria","Remo Freuler","Johan Manzambi","Granit Xhaka","Ardon Jashari","Djibril Sow","Christian Fassnacht","Michel Aebischer","Fabian Rieder","Breel Embolo","Dan Ndoye","Rubén Vargas","Noah Okafor","Zeki Amdouni","Cedric Itten"],
  "Brazil": ["Alisson","Weverton","Ederson","Wesley","Gabriel Magalhães","Marquinhos","Alex Sandro","Danilo Luiz","Bremer","Léo Pereira","Douglas Santos","Roger Ibañez","Casemiro","Bruno Guimarães","Fabinho","Danilo Santos","Lucas Paquetá","Vinícius Júnior","Matheus Cunha","Neymar","Raphinha","Endrick","Luiz Henrique","Gabriel Martinelli","Igor Thiago","Rayan"],
  "Haiti": ["Johny Placide","Alexandre Pierre","Josué Duverger","Ricardo Adé","Carlens Arcus","Martin Expérience","Jean-Kévin Duverne","Duke Lacroix","Wilguens Paugain","Hannes Delcroix","Keeto Thermoncy","Leverton Pierre","Danley Jean Jacques","Carl Sainté","Jean-Ricner Bellegarde","Woodensky Pierre","Dominique Simon","Duckens Nazon","Frantzdy Pierrot","Derrick Etienne Jr.","Louicius Deedson","Ruben Providence","Josué Casimir","Yassin Fortuné","Wilson Isidor","Lenny Joseph"],
  "Morocco": ["Yassine Bounou","Munir Mohamedi","Ahmed Reda Tagnaouti","Achraf Hakimi","Nayef Aguerd","Noussair Mazraoui","Youssef Belammari","Anass Salah-Eddine","Chadi Riad","Issa Diop","Zakaria El Ouahdi","Redouane Halhal","Sofyan Amrabat","Azzedine Ounahi","Bilal El Khannouss","Ismael Saibari","Neil El Aynaoui","Samir El Mourabet","Ayyoub Bouaddi","Ayoub El Kaabi","Soufiane Rahimi","Abde Ezzalzouli","Brahim Díaz","Chemsdine Talbi","Gessime Yassine","Ayoube Amaimouni"],
  "Scotland": ["Craig Gordon","Angus Gunn","Liam Kelly","Andy Robertson","Grant Hanley","Kieran Tierney","Scott McKenna","Jack Hendry","Nathan Patterson","Anthony Ralston","John Souttar","Aaron Hickey","Dominic Hyam","John McGinn","Scott McTominay","Ryan Christie","Kenny McLean","Lewis Ferguson","Ben Gannon-Doak","Findlay Curtis","Tyler Fletcher","Lyndon Dykes","Ché Adams","Lawrence Shankland","George Hirst","Ross Stewart"],
  "Australia": ["Mathew Ryan","Paul Izzo","Patrick Beach","Miloš Degenek","Alessandro Circati","Jacob Italiano","Jordan Bos","Jason Geria","Kai Trewin","Aziz Behich","Harry Souttar","Cameron Burgess","Lucas Herrington","Connor Metcalfe","Ajdin Hrustic","Aiden O'Neill","Cammy Devlin","Jackson Irvine","Paul Okon-Engstler","Mathew Leckie","Mohamed Touré","Awer Mabil","Nestory Irankunda","Nishan Velupillay","Cristian Volpato","Tete Yengi"],
  "Paraguay": ["Gatito Fernández","Orlando Gill","Gastón Olveira","Gustavo Gómez","Júnior Alonso","Fabián Balbuena","Omar Alderete","Juan José Cáceres","Gustavo Velázquez","José Canale","Alexandro Maidana","Miguel Almirón","Kaku","Andrés Cubas","Ramón Sosa","Diego Gómez","Damián Bobadilla","Braian Ojeda","Matías Galarza","Maurício","Antonio Sanabria","Julio Enciso","Gabriel Ávalos","Álex Arce","Isidro Pitta","Gustavo Caballero"],
  "Turkey": ["Uğurcan Çakır","Mert Günok","Altay Bayındır","Ersin Destanoğlu","Muhammed Şengezer","Merih Demiral","Zeki Çelik","Çağlar Söyüncü","Mert Müldür","Ferdi Kadıoğlu","Ozan Kabak","Abdülkerim Bardakcı","Eren Elmalı","Samet Akaydin","Yusuf Akçiçek","Mustafa Eskihellaç","Ahmetcan Kaplan","Hakan Çalhanoğlu","Kaan Ayhan","Orkun Kökçü","İsmail Yüksek","Salih Özcan","Atakan Karazor","Demir Ege Tıknaz","Kerem Aktürkoğlu","İrfan Can Kahveci","Barış Alper Yılmaz","Arda Güler","Kenan Yıldız","Yunus Akgün","Oğuz Aydın","Deniz Gül","Yusuf Sarı","Can Uzun","Aral Şimşir"],
  "USA": ["Matt Turner","Matt Freese","Chris Brady","Sergiño Dest","Chris Richards","Antonee Robinson","Auston Trusty","Miles Robinson","Tim Ream","Alex Freeman","Maximilian Arfsten","Mark McKenzie","Joe Scally","Tyler Adams","Giovanni Reyna","Weston McKennie","Sebastian Berhalter","Cristian Roldan","Malik Tillman","Ricardo Pepi","Christian Pulisic","Brenden Aaronson","Haji Wright","Folarin Balogun","Timothy Weah","Alejandro Zendejas"],
  "Curaçao": ["Eloy Room","Tyrick Bodak","Trevor Doornbusch","Shurandy Sambo","Juriën Gaari","Roshon van Eijma","Sherel Floranus","Armando Obispo","Joshua Brenet","Riechedly Bazoer","Deveron Fonville","Godfried Roemeratoe","Juninho Bacuna","Liviano Comenencia","Leandro Bacuna","Tyrese Noslin","Ar'jany Martha","Kevin Felida","Jürgen Locadia","Jeremy Antonisse","Sontje Hansen","Kenji Gorré","Jearl Margaritha","Brandley Kuwas","Gervane Kastaneer","Tahith Chong"],
  "Ecuador": ["Hernán Galíndez","Moisés Ramírez","Gonzalo Valle","Félix Torres","Piero Hincapié","Joel Ordóñez","Willian Pacho","Pervis Estupiñán","Ángelo Preciado","Jackson Porozo","Jordy Alcívar","Denil Castillo","John Yeboah","Kendry Páez","Moisés Caicedo","Alan Franco","Pedro Vite","Alan Minda","Yaimar Medina","Gonzalo Plata","Enner Valencia","Kevin Rodríguez","Anthony Valencia","Jordy Caicedo","Nilson Angulo","Jeremy Arévalo"],
  "Germany": ["Manuel Neuer","Oliver Baumann","Alexander Nübel","Antonio Rüdiger","Waldemar Anton","Jonathan Tah","Nico Schlotterbeck","David Raum","Nathaniel Brown","Malick Thiaw","Aleksandar Pavlović","Joshua Kimmich","Leon Goretzka","Jamie Leweling","Jamal Musiala","Pascal Groß","Angelo Stiller","Florian Wirtz","Leroy Sané","Nadiem Amiri","Felix Nmecha","Lennart Karl","Kai Havertz","Nick Woltemade","Maximilian Beier","Deniz Undav"],
  "Ivory Coast": ["Yahia Fofana","Alban Lafont","Mohamed Koné","Ghislain Konan","Odilon Kossounou","Wilfried Singo","Evan Ndicka","Emmanuel Agbadou","Guéla Doué","Ousmane Diomande","Christopher Opéri","Franck Kessié","Jean Michaël Seri","Ibrahim Sangaré","Seko Fofana","Christ Inao Oulaï","Parfait Guiagon","Nicolas Pépé","Oumar Diakité","Simon Adingra","Evann Guessand","Amad Diallo","Yan Diomande","Bazoumana Touré","Elye Wahi","Ange-Yoan Bonny"],
  "Japan": ["Zion Suzuki","Keisuke Ōsako","Tomoki Hayakawa","Yukinari Sugawara","Shōgo Taniguchi","Kō Itakura","Yūto Nagatomo","Tsuyoshi Watanabe","Hiroki Itō","Takehiro Tomiyasu","Ayumu Seko","Junnosuke Suzuki","Wataru Endo","Ao Tanaka","Takefusa Kubo","Ritsu Dōan","Keito Nakamura","Junya Itō","Daichi Kamada","Kaishū Sano","Keisuke Gotō","Daizen Maeda","Yuito Suzuki","Ayase Ueda","Kōki Ogawa","Kento Shiogai"],
  "Netherlands": ["Bart Verbruggen","Mark Flekken","Robin Roefs","Virgil van Dijk","Denzel Dumfries","Nathan Aké","Jurriën Timber","Micky van de Ven","Mats Wieffer","Jan Paul van Hecke","Jorrel Hato","Frenkie de Jong","Marten de Roon","Tijjani Reijnders","Teun Koopmeiners","Ryan Gravenberch","Justin Kluivert","Quinten Timber","Guus Til","Memphis Depay","Wout Weghorst","Donyell Malen","Cody Gakpo","Noa Lang","Brian Brobbey","Crysencio Summerville"],
  "Sweden": ["Jacob Widell Zetterström","Viktor Johansson","Kristoffer Nordfeldt","Gustaf Lagerbielke","Victor Lindelöf","Isak Hien","Gabriel Gudmundsson","Herman Johansson","Daniel Svensson","Hjalmar Ekdal","Carl Starfelt","Elliot Stroud","Lucas Bergvall","Jesper Karlström","Yasin Ayari","Mattias Svanberg","Besfort Zeneli","Alexander Isak","Benjamin Nygren","Anthony Elanga","Ken Sema","Viktor Gyökeres","Alexander Bernhardsson","Gustaf Nilsson","Taha Ali","Emil Holm"],
  "Tunisia": ["Aymen Dahmen","Sabri Ben Hessen","Mouhib Chamakh","Montassar Talbi","Dylan Bronn","Ali Abdi","Yan Valery","Mohamed Amine Ben Hamida","Moutaz Neffati","Omar Rekik","Adem Arous","Raed Chikhaoui","Ellyes Skhiri","Hannibal Mejbri","Anis Ben Slimane","Mortadha Ben Ouanes","Ismaël Gharbi","Hadj Mahmoud","Rani Khedira","Elias Achouri","Firas Chaouat","Hazem Mastouri","Elias Saad","Sebastian Tounekti","Khalil Ayari","Rayan Elloumi"],
  "Belgium": ["Thibaut Courtois","Senne Lammens","Mike Penders","Thomas Meunier","Timothy Castagne","Arthur Theate","Zeno Debast","Maxim De Cuyper","Brandon Mechele","Koni De Winter","Joaquin Seys","Nathan Ngoy","Axel Witsel","Kevin De Bruyne","Youri Tielemans","Hans Vanaken","Amadou Onana","Nicolas Raskin","Romelu Lukaku","Leandro Trossard","Jérémy Doku","Dodi Lukébakio","Charles De Ketelaere","Alexis Saelemaekers","Diego Moreira","Matias Fernandez-Pardo"],
  "Egypt": ["Mohamed El Shenawy","Mostafa Shobeir","Mohamed Alaa","El Mahdy Soliman","Hamdy Fathy","Ramy Rabia","Mohamed Hany","Ahmed Fatouh","Mohamed Abdelmonem","Yasser Ibrahim","Hossam Abdelmaguid","Karim Hafez","Tarek Alaa","Marwan Attia","Emam Ashour","Mohanad Lasheen","Mahmoud Saber","Nabil Emad","Mostafa Ziko","Mohamed Salah","Trézéguet","Zizo","Omar Marmoush","Ibrahim Adel","Haissem Hassan","Hamza Abdelkarim"],
  "Iran": ["Alireza Beiranvand","Payam Niazmand","Hossein Hosseini","Ehsan Hajsafi","Milad Mohammadi","Ramin Rezaeian","Hossein Kanaanizadegan","Shojae Khalilzadeh","Saleh Hardani","Ali Nemati","Danial Eiri","Alireza Jahanbakhsh","Saeid Ezatolahi","Saman Ghoddos","Mehdi Torabi","Rouzbeh Cheshmi","Mohammad Mohebi","Mehdi Ghayedi","Mohammad Ghorbani","Aria Yousefi","Amirmohammad Razzaghinia","Mehdi Taremi","Shahriyar Moghanlou","Amirhossein Hosseinzadeh","Ali Alipour","Dennis Eckert"],
  "New Zealand": ["Max Crocombe","Alex Paulsen","Michael Woud","Tim Payne","Francis de Vries","Tyler Bindon","Michael Boxall","Liberato Cacace","Nando Pijnaker","Finn Surman","Callan Elliot","Tommy Smith","Joe Bell","Matthew Garbett","Marko Stamenić","Sarpreet Singh","Elijah Just","Alex Rufer","Ben Old","Callum McCowatt","Ryan Thomas","Lachlan Bayliss","Chris Wood","Kosta Barbarouses","Ben Waine","Jesse Randall"],
  "Cape Verde": ["Vozinha","Márcio Rosa","CJ dos Santos","Stopira","Roberto Lopes","João Paulo","Diney","Logan Costa","Steven Moreira","Wagner Pina","Sidny Lopes Cabral","Kelvin Pires","Jamiro Monteiro","Kevin Pina","Deroy Duarte","Telmo Arcanjo","Laros Duarte","Yannick Semedo","Ryan Mendes","Garry Rodrigues","Willy Semedo","Jovane Cabral","Gilson Benchimol","Dailon Livramento","Hélio Varela","Nuno da Costa"],
  "Saudi Arabia": ["Mohammed Al-Owais","Nawaf Al-Aqidi","Ahmed Al-Kassar","Saud Abdulhamid","Hassan Al-Tambakti","Abdulelah Al-Amri","Nawaf Boushal","Ali Lajami","Ali Majrashi","Hassan Kadesh","Moteb Al-Harbi","Jehad Thakri","Mohammed Abu Al-Shamat","Salem Al-Dawsari","Mohamed Kanno","Nasser Al-Dawsari","Abdullah Al-Khaibari","Musab Al-Juwayr","Ayman Yahya","Ziyad Al-Johani","Sultan Mandash","Alaa Al-Hejji","Firas Al-Buraikan","Saleh Al-Shehri","Abdullah Al-Hamdan","Khalid Al-Ghannam"],
  "Spain": ["David Raya","Joan Garcia","Unai Simón","Marc Pubill","Álex Grimaldo","Eric García","Marcos Llorente","Pedro Porro","Aymeric Laporte","Pau Cubarsí","Marc Cucurella","Mikel Merino","Fabián Ruiz","Gavi","Álex Baena","Rodri","Martín Zubimendi","Pedri","Ferran Torres","Dani Olmo","Yéremy Pino","Nico Williams","Lamine Yamal","Mikel Oyarzabal","Víctor Muñoz","Borja Iglesias"],
  "Uruguay": ["Fernando Muslera","Sergio Rochet","Santiago Mele","José María Giménez","Matías Viña","Mathías Olivera","Guillermo Varela","Ronald Araújo","Sebastián Cáceres","Joaquín Piquerez","Santiago Bueno","Rodrigo Bentancur","Federico Valverde","Giorgian de Arrascaeta","Facundo Pellistri","Manuel Ugarte","Nicolás de la Cruz","Brian Rodríguez","Maximiliano Araújo","Agustín Canobbio","Emiliano Martínez","Rodrigo Zalazar","Juan Manuel Sanabria","Darwin Núñez","Federico Viñas","Rodrigo Aguirre"],
  "France": ["Brice Samba","Mike Maignan","Robin Risser","Malo Gusto","Lucas Digne","Dayot Upamecano","Jules Koundé","Ibrahima Konaté","William Saliba","Théo Hernandez","Lucas Hernandez","Maxence Lacroix","Manu Koné","Aurélien Tchouaméni","N'Golo Kanté","Adrien Rabiot","Warren Zaïre-Emery","Ousmane Dembélé","Marcus Thuram","Kylian Mbappé","Michael Olise","Bradley Barcola","Jean-Philippe Mateta","Désiré Doué","Rayan Cherki","Maghnes Akliouche"],
  "Iraq": ["Jalal Hassan","Fahad Talib","Ahmed Basil","Rebin Sulaka","Manaf Younis","Merchas Doski","Zaid Tahseen","Frans Putros","Hussein Ali","Ahmed Yahya","Mustafa Saadoon","Akam Hashim","Ibrahim Bayesh","Amir Al-Ammari","Ali Jasim","Youssef Amyn","Zidane Iqbal","Marko Farji","Kevin Yakob","Aimar Sher","Zaid Ismail","Ahmed Qasem","Aymen Hussein","Mohanad Ali","Ali Al-Hamadi","Ali Yousif"],
  "Norway": ["Ørjan Nyland","Sander Tangvik","Egil Selvik","Kristoffer Ajer","Leo Østigård","David Møller Wolfe","Marcus Holmgren Pedersen","Torbjørn Heggem","Fredrik André Bjørkan","Sondre Langås","Henrik Falchener","Julian Ryerson","Morten Thorsby","Patrick Berg","Sander Berge","Fredrik Aursnes","Kristian Thorstvedt","Thelo Aasgaard","Antonio Nusa","Andreas Schjelderup","Oscar Bobb","Jens Petter Hauge","Alexander Sørloth","Erling Haaland","Jørgen Strand Larsen","Martin Ødegaard"],
  "Senegal": ["Édouard Mendy","Mory Diaw","Yehvann Diouf","Kalidou Koulibaly","Krépin Diatta","Moussa Niakhaté","Ismail Jakobs","Abdoulaye Seck","El Hadji Malick Diouf","Mamadou Sarr","Antoine Mendy","Ilay Camara","Moustapha Mbow","Idrissa Gueye","Pape Gueye","Pape Matar Sarr","Lamine Camara","Pathé Ciss","Habib Diarra","Bara Sapoko Ndiaye","Sadio Mané","Ismaïla Sarr","Iliman Ndiaye","Nicolas Jackson","Bamba Dieng","Cherif Ndiaye","Ibrahim Mbaye","Assane Diao"],
  "Algeria": ["Luca Zidane","Oussama Benbot","Melvin Mastil","Aïssa Mandi","Ramy Bensebaini","Mohamed Amine Tougai","Rayan Aït-Nouri","Jaouen Hadjam","Rafik Belghali","Zineddine Belaïd","Achref Abada","Samir Chergui","Nabil Bentaleb","Ramiz Zerrouki","Hicham Boudaoui","Farès Chaïbi","Houssem Aouar","Ibrahim Maza","Yacine Titraoui","Riyad Mahrez","Mohamed Amoura","Amine Gouiri","Anis Hadj Moussa","Adil Boulbina","Nadhir Benbouali","Farès Ghedjemis"],
  "Argentina": ["Juan Musso","Gerónimo Rulli","Emiliano Martínez","Leonardo Balerdi","Nicolás Tagliafico","Gonzalo Montiel","Lisandro Martínez","Cristian Romero","Nicolás Otamendi","Facundo Medina","Nahuel Molina","Leandro Paredes","Rodrigo De Paul","Valentín Barco","Exequiel Palacios","Alexis Mac Allister","Enzo Fernández","Giovani Lo Celso","Julián Alvarez","Lionel Messi","Nicolás González","Thiago Almada","Giuliano Simeone","Nico Paz","José Manuel López","Lautaro Martínez"],
  "Austria": ["Alexander Schlager","Florian Wiegele","Patrick Pentz","David Affengruber","Kevin Danso","Stefan Posch","David Alaba","Philipp Lienhart","Phillipp Mwene","Alexander Prass","Marco Friedl","Michael Svoboda","Xaver Schlager","Nicolas Seiwald","Florian Grillitsch","Marcel Sabitzer","Romano Schmid","Konrad Laimer","Patrick Wimmer","Carney Chukwuemeka","Paul Wanner","Alessandro Schöpf","Marko Arnautović","Michael Gregoritsch","Saša Kalajdžić","Christoph Baumgartner"],
  "Jordan": ["Yazeed Abulaila","Abdallah Al-Fakhouri","Nour Bani Attiah","Ihsan Haddad","Yazan Al-Arab","Abdallah Nasib","Saed Al-Rosan","Husam Abu Dahab","Mo Abualnadi","Salim Obaid","Anas Badawi","Rajaei Ayed","Noor Al-Rawabdeh","Ibrahim Sadeh","Mohammad Abu Hashish","Nizar Al-Rashdan","Mohannad Abu Taha","Amer Jamous","Mohammad Al-Dawoud","Yousef Qashi","Mohammad Taha","Musa Al-Taamari","Mahmoud Al-Mardi","Ali Olwan","Mohammad Abu Zrayq","Odeh Al-Fakhouri","Ibrahim Sabra","Ali Azaizeh"],
  "Colombia": ["David Ospina","Camilo Vargas","Álvaro Montero","Davinson Sánchez","Santiago Arias","Yerry Mina","Daniel Muñoz","Johan Mojica","Jhon Lucumí","Deiver Machado","Willer Ditta","James Rodríguez","Jefferson Lerma","Juan Fernando Quintero","Jhon Arias","Richard Ríos","Kevin Castaño","Jorge Carrascal","Jaminton Campaz","Juan Portilla","Gustavo Puerta","Luis Díaz","Jhon Córdoba","Luis Suárez","Cucho Hernández","Andrés Gómez"],
  "DR Congo": ["Lionel Mpasi","Timothy Fayulu","Matthieu Epolo","Chancel Mbemba","Arthur Masuaku","Gédéon Kalulu","Joris Kayembe","Dylan Batubinsika","Axel Tuanzebe","Aaron Wan-Bissaka","Steve Kapuadi","Samuel Moutoussamy","Edo Kayembe","Charles Pickel","Gaël Kakuta","Noah Sadiki","Aaron Tshibola","Ngal'ayel Mukau","Brian Cipenga","Cédric Bakambu","Meschak Elia","Théo Bongonda","Fiston Mayele","Yoane Wissa","Nathanaël Mbuku","Simon Banza"],
  "Portugal": ["Diogo Costa","José Sá","Rui Silva","Rúben Dias","João Cancelo","Nélson Semedo","Nuno Mendes","Diogo Dalot","Gonçalo Inácio","Matheus Nunes","Renato Veiga","Tomás Araújo","Bernardo Silva","Bruno Fernandes","Rúben Neves","Vitinha","João Neves","Samú Costa","Cristiano Ronaldo","João Félix","Rafael Leão","Gonçalo Guedes","Gonçalo Ramos","Pedro Neto","Francisco Trincão","Francisco Conceição"],
  "Uzbekistan": ["Utkir Yusupov","Abduvohid Nematov","Botirali Ergashev","Rustam Ashurmatov","Farrukh Sayfiev","Khojiakbar Alijonov","Sherzod Nasrullaev","Umar Eshmurodov","Abdukodir Khusanov","Abdulla Abdullaev","Bekhruz Karimov","Jakhongir Urozov","Avazbek Ulmasaliev","Otabek Shukurov","Odiljon Hamrobekov","Jamshid Iskanderov","Akmal Mozgovoy","Azizjon Ganiev","Jasurbek Jaloliddinov","Umarali Rakhmonaliev","Sherzod Esanov","Eldor Shomurodov","Igor Sergeev","Jaloliddin Masharipov","Oston Urunov","Dostonbek Khamdamov","Abbosbek Fayzullaev","Azizbek Amonov","Ruslanbek Jiyanov","Sherzod Temirov"],
  "Croatia": ["Dominik Livaković","Dominik Kotarski","Ivor Pandur","Joško Gvardiol","Duje Ćaleta-Car","Josip Šutalo","Josip Stanišić","Marin Pongračić","Martin Erlić","Luka Vušković","Luka Modrić","Mateo Kovačić","Mario Pašalić","Nikola Vlašić","Luka Sučić","Martin Baturina","Kristijan Jakić","Petar Sučić","Nikola Moro","Toni Fruk","Ivan Perišić","Andrej Kramarić","Ante Budimir","Marco Pašalić","Petar Musa","Igor Matanović"],
  "England": ["Jordan Pickford","Dean Henderson","James Trafford","John Stones","Marc Guéhi","Reece James","Ezri Konsa","Dan Burn","Tino Livramento","Djed Spence","Nico O'Reilly","Jarell Quansah","Jordan Henderson","Declan Rice","Jude Bellingham","Morgan Rogers","Kobbie Mainoo","Elliot Anderson","Harry Kane","Marcus Rashford","Bukayo Saka","Ollie Watkins","Anthony Gordon","Eberechi Eze","Noni Madueke","Ivan Toney"],
  "Ghana": ["Lawrence Ati-Zigi","Benjamin Asare","Joseph Anang","Abdul Rahman Baba","Gideon Mensah","Alidu Seidu","Jerome Opoku","Jonas Adjetey","Abdul Mumin","Kojo Peprah Oppong","Derrick Luckassen","Marvin Senaya","Thomas Partey","Abdul Fatawu","Elisha Owusu","Caleb Yirenkyi","Kwasi Sibo","Augustine Boakye","Jordan Ayew","Antoine Semenyo","Kamaldeen Sulemana","Iñaki Williams","Ernest Nuamah","Christopher Bonsu Baah","Brandon Thomas-Asante","Prince Kwabena Adu"],
  "Panama": ["Luis Mejía","Orlando Mosquera","César Samudio","Eric Davis","Fidel Escobar","Michael Amir Murillo","Roderick Miller","Andrés Andrade","César Blackman","José Córdoba","Jiovany Ramos","Jorge Gutiérrez","Edgardo Fariña","Aníbal Godoy","Alberto Quintero","Yoel Bárcenas","Adalberto Carrasquilla","José Luis Rodríguez","Cristian Martínez","César Yanis","Carlos Harvey","Azarias Londoño","José Fajardo","Ismael Díaz","Cecilio Waterman","Tomás Rodríguez"],
}

# Build flat set of all official players (lowercase for comparison)
all_official_players = set()
player_to_team = {}
for team, players in OFFICIAL_SQUADS.items():
  for p in players:
    all_official_players.add(p.lower())
    player_to_team[p.lower()] = team

def is_official_player(name):
  return name.lower() in all_official_players

# --- Call Claude with web search ---
payload = {
  "model": "claude-sonnet-4-5",
  "max_tokens": 4000,
  "tools": [{"type": "web_search_20250305", "name": "web_search"}],
  "system": f"""You are a football journalist covering FIFA World Cup 2026. Today is {today}.
Search the web for injury news about players in the official FIFA World Cup 2026 squads.
After searching, wrap your JSON result in <injuries> tags like this:
<injuries>[{{"player":string,"team":string,"flag":string,"pos":string,"club":string,"status":"out"|"doubt","injury":string,"replacement":string|null,"timeline":string|null,"link":string,"link_label":string,"confirmed_date":string}}]</injuries>
The JSON must be inside <injuries> tags. Do not put any text inside the tags except the JSON array.""",
  "messages": [{
    "role": "user",
    "content": f"Today is {today}. Search for FIFA World Cup 2026 injury news. Search: 'World Cup 2026 injury withdrawal', 'FIFA World Cup 2026 injured players', 'Mundial 2026 lesionados'. Then wrap the JSON array inside <injuries> tags."
  }]
}

req = urllib.request.Request(
  'https://api.anthropic.com/v1/messages',
  data=json.dumps(payload).encode(),
  headers={
    'Content-Type': 'application/json',
    'x-api-key': ANTHROPIC_API_KEY,
    'anthropic-version': '2023-06-01'
  }
)

with urllib.request.urlopen(req, timeout=300) as resp:
  data = json.loads(resp.read())

texts = []
for block in data.get('content', []):
  if block.get('type') == 'text':
    texts.append(block.get('text', ''))

full_text = '\n'.join(texts)
print("Claude response (first 300 chars):", full_text[:300])

# Extract JSON - try <injuries> tags first, then fallback
players = []
json_str = ''
tag_match = re.search(r'<injuries>([\s\S]*?)</injuries>', full_text)
if tag_match:
  json_str = tag_match.group(1).strip()
  json_str = re.sub(r'```json\s*', '', json_str)
  json_str = re.sub(r'```\s*', '', json_str).strip()
  print("Found <injuries> tags")
else:
  clean_text = re.sub(r'```json\s*', '', full_text)
  clean_text = re.sub(r'```\s*', '', clean_text)
  start = clean_text.find('[')
  end = clean_text.rfind(']')
  if start != -1 and end != -1:
    json_str = clean_text[start:end+1]
  print("WARNING: No <injuries> tags, using fallback")

if json_str:
  try:
    raw_players = json.loads(json_str)
    # FILTER: only keep players in official squads
    for p in raw_players:
      if p.get('status') in ('out', 'doubt') and is_official_player(p.get('player', '')):
        players.append(p)
      elif p.get('status') in ('out', 'doubt'):
        print(f"FILTERED OUT (not in official squad): {p.get('player')} ({p.get('team')})")
    print(f"Found {len(players)} official squad players with injuries")
  except Exception as e:
    print(f"ERROR parsing JSON: {e}")
    print(f"JSON string (first 200): {json_str[:200]}")

# --- Get previous data from KV ---
kv_url = f'https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{CF_KV_NAMESPACE_ID}/values/injury_data'
kv_headers = {'Authorization': f'Bearer {CF_API_TOKEN}'}

prev_data = []
update_count = 0
try:
  req2 = urllib.request.Request(kv_url, headers=kv_headers)
  with urllib.request.urlopen(req2, timeout=10) as resp:
    cached = json.loads(resp.read())
    prev_data = cached.get('data', [])
    update_count = cached.get('updateCount', 0)
except Exception as e:
  print(f"No previous KV data: {e}")

update_count += 1

# --- Detect changes ---
alerts = []
prev_map = {p['player']: p for p in prev_data}

for p in players:
  old = prev_map.get(p['player'])
  if not old:
    emoji = '🚨' if p['status'] == 'out' else '⚠️'
    status_text = 'CONFIRMED OUT' if p['status'] == 'out' else 'INJURY DOUBT'
    alerts.append(
      f"{emoji} <b>NEW INJURY — {status_text}</b>\n\n"
      f"👤 <b>{p['player']}</b> {p.get('flag','')}\n"
      f"🏳️ {p.get('team','')} · {p.get('pos','')}\n"
      f"🩹 {p.get('injury','')}\n"
      f"⏱ {p.get('timeline','Timeline unknown')}\n"
      + (f"↪️ Replaced by: {p['replacement']}\n" if p.get('replacement') else '')
      + "\n🌐 wc2026-injuries.prohaskajoaquin.workers.dev"
    )
  elif old.get('status') != p.get('status'):
    emoji = '🚨' if p['status'] == 'out' else '✅'
    alerts.append(
      f"{emoji} <b>STATUS CHANGE</b>\n\n"
      f"👤 <b>{p['player']}</b> {p.get('flag','')}\n"
      f"📊 {old.get('status','').upper()} → {p.get('status','').upper()}\n"
      f"🩹 {p.get('injury','')}\n"
      + "\n🌐 wc2026-injuries.prohaskajoaquin.workers.dev"
    )

def send_telegram(text):
  if not TELEGRAM_BOT_TOKEN:
    return
  tg_payload = json.dumps({
    'chat_id': '@wc2026injuryalerts',
    'text': text,
    'parse_mode': 'HTML',
    'disable_web_page_preview': True
  }).encode()
  tg_req = urllib.request.Request(
    f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
    data=tg_payload,
    headers={'Content-Type': 'application/json'}
  )
  try:
    with urllib.request.urlopen(tg_req, timeout=10) as r:
      print(f"Telegram sent: {r.status}")
  except Exception as e:
    print(f"Telegram error: {e}")

for alert in alerts:
  send_telegram(alert)

# --- Save to KV ---
kv_value = json.dumps({
  'data': players,
  'lastUpdated': int(time.time() * 1000),
  'updateCount': update_count
}).encode()

put_req = urllib.request.Request(
  kv_url,
  data=kv_value,
  headers={**kv_headers, 'Content-Type': 'application/json'},
  method='PUT'
)
with urllib.request.urlopen(put_req, timeout=10) as resp:
  result = json.loads(resp.read())
  print(f"KV write: {result}")

out_count = len([p for p in players if p.get('status') == 'out'])
doubt_count = len([p for p in players if p.get('status') == 'doubt'])
print(f"✅ Update #{update_count} — {len(players)} players ({out_count} out, {doubt_count} doubt). {len(alerts)} alerts.")

summary = (
  f"🤖 <b>WC2026 Injury Tracker — Update #{update_count}</b>\n\n"
  f"🚨 Confirmed out: <b>{out_count}</b>\n"
  f"⚠️ Doubt: <b>{doubt_count}</b>\n"
  f"📊 Total tracked: <b>{len(players)}</b>\n\n"
  f"🌐 wc2026-injuries.prohaskajoaquin.workers.dev"
)
send_telegram(summary)
