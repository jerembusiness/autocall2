import telebot
import json
import random
import time
import threading
from telebot import types

TOKEN = "7565087345:AAFoSOxn_vuuSruc0aQ6yyvaRz627zIYFZM"  # Remplace par le token de ton bot
ADMIN_ID = 5178571088  # Remplace par ton ID Telegram (tu peux l'obtenir via @userinfobot)

bot = telebot.TeleBot(TOKEN)

# Charger ou initialiser la base de données
FICHIER_JSON = "data.json"

try:
    with open(FICHIER_JSON, "r") as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}
except Exception as e:
    print(f"Erreur lors du chargement de la base de données : {e}")
    users = {}

# Sauvegarder les données dans le fichier JSON
def sauvegarder():
    try:
        with open(FICHIER_JSON, "w") as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données : {e}")

# Dictionnaire de traductions
translations = {
    "fr": {
        "menu": "👋 Salut ! Bienvenue sur mon bot. Choisis une option ci-dessous :",
        "info_conso": "📊 Voir ma consommation",
        "start_call": "📞 Commencer un appel",
        "withdraw": "💸 Demander un retrait",
        "add_credits": "➕ Ajouter des crédits",
        "clients": "👥 Voir les clients",
        "validate_withdraw": "✅ Valider un retrait",
        "add_credits_message": "👉 Pour ajouter des crédits, contacte-moi ici : @boostcommunauter",
        "choose_language": "🌍 Choisissez votre langue",
        "admin_add_credits": "🔑 Ajouter des crédits à un utilisateur",
        "admin_add_euros": "💶 Ajouter des Euros à un utilisateur"  # Nouveau texte pour ajouter des euros
    },
    "en": {
        "menu": "👋 Hi! Welcome to my bot. Choose an option below:",
        "info_conso": "📊 View my consumption",
        "start_call": "📞 Start a call",
        "withdraw": "💸 Request a withdrawal",
        "add_credits": "➕ Add credits",
        "clients": "👥 View the clients",
        "validate_withdraw": "✅ Validate a withdrawal",
        "add_credits_message": "👉 To add credits, contact me here: @boostcommunauter",
        "choose_language": "🌍 Choose your language",
        "admin_add_credits": "🔑 Add credits to a user",
        "admin_add_euros": "💶 Add Euros to a user"  # New text for adding euros
    }
}

# Créer le menu principal avec des boutons
def create_main_menu(user_id):
    # Si l'utilisateur n'existe pas encore, on l'ajoute à la base de données avec une langue par défaut (fr)
    if str(user_id) not in users:
        users[str(user_id)] = {"credits": 0, "euros": 0, "withdraw_requested": False, "language": "fr"}
        sauvegarder()

    user_language = users[str(user_id)].get("language", "fr")

    keyboard = types.InlineKeyboardMarkup(row_width=1)  # 1 bouton par ligne
    # Ajouter les boutons de commandes principales
    button_info_conso = types.InlineKeyboardButton(text=translations[user_language]["info_conso"], callback_data="info_conso")
    button_start_call = types.InlineKeyboardButton(text=translations[user_language]["start_call"], callback_data="start_call")
    button_withdraw = types.InlineKeyboardButton(text=translations[user_language]["withdraw"], callback_data="withdraw")

    # Ajouter un bouton pour "Ajouter des crédits"
    button_add_credits = types.InlineKeyboardButton(text=translations[user_language]["add_credits"], callback_data="add_credits")

    # Ajouter un bouton pour "Ajouter des Euros" (disponible pour les administrateurs)
    if is_admin(user_id):
        button_admin_add_credits = types.InlineKeyboardButton(text=translations[user_language]["admin_add_credits"], callback_data="admin_add_credits")  # Ajout du bouton admin
        button_admin_add_euros = types.InlineKeyboardButton(text=translations[user_language]["admin_add_euros"], callback_data="admin_add_euros")  # Ajout du bouton admin pour les euros
        button_clients = types.InlineKeyboardButton(text=translations[user_language]["clients"], callback_data="clients")
        button_validate_withdraw = types.InlineKeyboardButton(text=translations[user_language]["validate_withdraw"], callback_data="validate_withdraw")
        keyboard.add(button_admin_add_credits, button_admin_add_euros, button_clients, button_validate_withdraw)

    # Ajouter les autres boutons
    keyboard.add(button_info_conso, button_start_call, button_withdraw, button_add_credits)

    # Ajouter un bouton de changement de langue uniquement pour les clients
    if not is_admin(user_id):
        button_language = types.InlineKeyboardButton(text=translations[user_language]["choose_language"], callback_data="choose_language")
        keyboard.add(button_language)

    return keyboard

# Vérifier si l'utilisateur est admin
def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

# Commande /start
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.chat.id
    # Créer le menu avec des boutons
    keyboard = create_main_menu(user_id)

    # Envoyer un message avec les boutons
    bot.send_message(
        message.chat.id,
        translations[users.get(str(user_id), {}).get('language', 'fr')]["menu"],
        reply_markup=keyboard
    )

# Gestion des actions sur les boutons
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.from_user.id

    # S'assurer que l'utilisateur existe dans la base de données
    if str(user_id) not in users:
        users[str(user_id)] = {"credits": 0, "euros": 0, "withdraw_requested": False, "language": "fr"}
        sauvegarder()

    if call.data == "info_conso":
        # Afficher la consommation
        user_id_str = str(user_id)
        if user_id_str not in users:
            bot.send_message(call.message.chat.id, "❌ Vous n'avez pas encore de crédits.")
        else:
            credits = users[user_id_str]["credits"]
            euros = users[user_id_str]["euros"]
            bot.send_message(call.message.chat.id, f"📊 *Votre consommation :*\n"
                                                   f"💰 Crédits restants : {credits}\n"
                                                   f"💳 Montant généré : {euros:.2f}€", parse_mode="Markdown")

    elif call.data == "start_call":
        # Démarrer un appel
        user_id_str = str(user_id)
        if user_id_str not in users or users[user_id_str]["credits"] <= 0:
            bot.send_message(call.message.chat.id, "❌ Vous n'avez pas assez de crédits.")
        else:
            bot.send_message(call.message.chat.id, "🔍 *Recherche d'accès IPRN en cours...*", parse_mode="Markdown")
            threading.Thread(target=debit_credits, args=(user_id_str,)).start()

    elif call.data == "withdraw":
        # Demander un retrait
        user_id_str = str(user_id)
        if user_id_str not in users or users[user_id_str]["euros"] < 5:
            bot.send_message(call.message.chat.id, "❌ Vous devez avoir au moins 5€ pour retirer.")
        else:
            users[user_id_str]["withdraw_requested"] = True
            sauvegarder()
            bot.send_message(ADMIN_ID, f"📢 *Demande de retrait !*\n\n👤 Utilisateur : {call.from_user.username}\n💳 Solde : {users[user_id_str]['euros']:.2f}€", parse_mode="Markdown")
            bot.send_message(call.message.chat.id, "✅ Demande envoyée. L'admin va traiter votre retrait.")

    elif call.data == "add_credits":
        # Envoyer ton contact Telegram pour que l'utilisateur te contacte pour ajouter des crédits
        bot.send_message(call.message.chat.id, translations[users.get(str(user_id), {}).get('language', 'fr')]["add_credits_message"])

    elif call.data == "admin_add_credits" and is_admin(user_id):
        # Ajouter des crédits à un utilisateur (admin seulement)
        bot.send_message(call.message.chat.id, "🔑 Entrez l'ID de l'utilisateur et le montant des crédits à ajouter (ex: 123456789 50 pour ajouter 50 crédits à l'utilisateur avec ID 123456789).")

        # Attendre la réponse de l'admin
        @bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID)
        def handle_add_credits_response(message):
            try:
                user_id_str, credits_to_add = message.text.split()
                user_id_str = str(user_id_str)
                credits_to_add = int(credits_to_add)
                if user_id_str in users:
                    users[user_id_str]["credits"] += credits_to_add
                    sauvegarder()
                    bot.send_message(call.message.chat.id, f"✅ {credits_to_add} crédits ont été ajoutés à l'utilisateur {user_id_str}.")
                else:
                    bot.send_message(call.message.chat.id, "❌ Utilisateur introuvable.")
            except Exception as e:
                bot.send_message(call.message.chat.id, "❌ Format incorrect, assurez-vous de bien suivre la syntaxe (ID Utilisateur Montant).")

    elif call.data == "admin_add_euros" and is_admin(user_id):
        # Ajouter des euros à un utilisateur (admin seulement)
        bot.send_message(call.message.chat.id, "🔑 Entrez l'ID de l'utilisateur et le montant des euros à ajouter (ex: 123456789 50 pour ajouter 50€ à l'utilisateur avec ID 123456789).")

        # Attendre la réponse de l'admin
        @bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID)
        def handle_add_euros_response(message):
            try:
                user_id_str, euros_to_add = message.text.split()
                user_id_str = str(user_id_str)
                euros_to_add = float(euros_to_add)
                if user_id_str in users:
                    users[user_id_str]["euros"] += euros_to_add
                    sauvegarder()
                    bot.send_message(call.message.chat.id, f"✅ {euros_to_add}€ ont été ajoutés à l'utilisateur {user_id_str}.")
                else:
                    bot.send_message(call.message.chat.id, "❌ Utilisateur introuvable.")
            except Exception as e:
                bot.send_message(call.message.chat.id, "❌ Format incorrect, assurez-vous de bien suivre la syntaxe (ID Utilisateur Montant).")

    elif call.data == "clients" and is_admin(user_id):
        # Afficher les clients (admin seulement)
        info = "📜 *Liste des clients :*\n\n"
        for user_id_str, data in users.items():
            info += f"👤 {user_id_str} | Crédits : {data['credits']} | Euros : {data['euros']:.2f}€\n"
        bot.send_message(call.message.chat.id, info, parse_mode="Markdown")

    elif call.data == "validate_withdraw" and is_admin(user_id):
        # Valider un retrait (admin seulement)
        bot.send_message(call.message.chat.id, "⚠️ Entrez l'ID ou le nom d'utilisateur de l'utilisateur pour valider le retrait (ex: '123456789' ou '@username').")

        # Attendre la réponse de l'admin
        @bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID)
        def handle_withdraw_validation(message):
            try:
                user_input = message.text.strip()  # Utilisateur entre l'ID ou le nom d'utilisateur
                if user_input.startswith('@'):  # Si c'est un nom d'utilisateur
                    username = user_input[1:]  # Retirer le '@'
                    user_id_str = str(bot.get_chat(username).id)  # Essayer d'obtenir l'ID avec le nom d'utilisateur
                else:  # Sinon, c'est un ID utilisateur
                    user_id_str = str(user_input)

                if user_id_str in users and users[user_id_str]["withdraw_requested"]:
                    users[user_id_str]["euros"] = 0
                    users[user_id_str]["withdraw_requested"] = False
                    sauvegarder()
                    bot.send_message(user_id_str, "✅ Votre retrait a été validé !")
                    bot.send_message(call.message.chat.id, f"✅ Retrait validé pour l'utilisateur {user_id_str}.")
                else:
                    bot.send_message(call.message.chat.id, "❌ Aucun retrait demandé ou utilisateur introuvable.")
            except Exception as e:
                bot.send_message(call.message.chat.id, f"❌ Erreur : {str(e)}")

    elif call.data == "choose_language":
        # Choisir la langue (Français / Anglais)
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        button_fr = types.InlineKeyboardButton(text="Français", callback_data="set_language_fr")
        button_en = types.InlineKeyboardButton(text="English", callback_data="set_language_en")
        keyboard.add(button_fr, button_en)
        bot.send_message(call.message.chat.id, "Veuillez choisir votre langue / Please choose your language:", reply_markup=keyboard)

    elif call.data == "set_language_fr":
        users[str(user_id)]["language"] = "fr"
        sauvegarder()
        bot.send_message(call.message.chat.id, "✅ La langue a été changée en Français.", reply_markup=create_main_menu(user_id))

    elif call.data == "set_language_en":
        users[str(user_id)]["language"] = "en"
        sauvegarder()
        bot.send_message(call.message.chat.id, "✅ Language has been changed to English.", reply_markup=create_main_menu(user_id))

# Fonction de débit automatique des crédits
def debit_credits(user_id):
    user_data = users[user_id]
    credits = user_data["credits"]

    # Définir la durée du débit en fonction des crédits
    if  1     <= credits <= 4999:
        days = 35
    elif 5000 <= credits <= 9999:
        days = 46
    elif 10000 <= credits <= 14999:
        days = 66
    elif 15000 <= credits <= 39999:
        days = 94
    elif 40000 <= credits <= 100000:
        days = 160
    else:
        bot.send_message(user_id, "❌ *Vous n'êtes pas éligible pour un débit automatique.*", parse_mode="Markdown")
        return

    # Calcul du nombre de minutes total sur la période
    total_minutes = days * 24 * 60
    debit_per_interval = credits / total_minutes  # Crédits débités par minute

    # Délai entre chaque débit (5 à 10 minutes)
    while user_data["credits"] > 0:
        time.sleep(random.randint(300, 600))  # Entre 5 et 10 minutes

        # Calcul des crédits à débiter à chaque intervalle
        debit = random.randint(1, 5)  # Débit aléatoire entre 1 et 5 crédits
        if user_data["credits"] < debit: 
            debit = user_data["credits"]

        # Débiter les crédits et calculer les gains en euros
        user_data["credits"] -= debit
        valeur_credit = random.uniform(0.01, 0.012)  # Valeur aléatoire du crédit entre 0.017 et 0.022 EUR
        user_data["euros"] += debit * valeur_credit

        # Sauvegarder les données
        sauvegarder()

        if user_data["credits"] == 0:
            bot.send_message(user_id, "🔴 *Crédits épuisés, appel terminé.*", parse_mode="Markdown")



# Lancer le bot
bot.polling()  

  