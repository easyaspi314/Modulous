from KerbalStuff.objects import Mod, ModVersion, User, Category
from KerbalStuff.database import db
from KerbalStuff.config import _cfg
from sqlalchemy import or_, and_, desc

import math

from datetime import datetime

def weigh_result(result, terms):
    # Factors considered, * indicates important factors:
    # Mods where several search terms match are given a dramatically higher rank*
    # High followers and high downloads get bumped*
    # Mods with a long version history get bumped
    # Mods with lots of screenshots or videos get bumped
    # Mods with a short description get docked
    # Mods lose points the longer they go without updates*
    # Mods get points for supporting the latest KSP version
    # Mods get points for being open source
    # New mods are given a hefty bonus to avoid drowning among established mods
    score = 0
    name_matches = short_matches = 0
    for term in terms:
        if result.name.lower().count(term) != 0:
            name_matches += 1
            score += name_matches * 100
        if result.short_description.lower().count(term) != 0:
            short_matches += 1
            score += short_matches * 50

    score *= 100

    score += result.follower_count * 10
    score += result.download_count
    score += len(result.versions) / 5
    score += len(result.media)
    if len(result.description) < 100:
        score -= 10
    if result.updated:
        delta = (datetime.now() - result.updated).days
        if delta > 100:
            delta = 100 # Don't penalize for oldness past a certain point
        score -= delta / 5
#    if len(result.versions) > 0:
#        if result.versions[0].ksp_version == _cfg("latest-ksp"):
#            score += 50
    if result.source_link:
        score += 10
    if (result.created - datetime.now()).days < 30:
        score += 100

    return score

def search_mods(text, page, limit, category=None):
    terms = text.split(' ')
    query = db.query(Mod).join(Mod.user).join(Mod.versions).join(Mod.category)
    filters = list()
    filtering_by_game = False
    filtering_by_category = False
    category_filtering_by = ""
    game_filtering_by = ""
    for term in terms:
        if term.startswith("game:"):
            filtering_by_game = True
            game_filtering_by = term[5:]
        elif term.startswith("user:"):
            filters.append(User.username == term[5:])
        elif term.startswith("downloads:>"):
            filters.append(Mod.download_count > int(term[11:]))
        elif term.startswith("downloads:<"):
            filters.append(Mod.download_count < int(term[11:]))
        elif term.startswith("followers:>"):
            filters.append(Mod.follower_count > int(term[11:]))
        elif term.startswith("followers:<"):
            filters.append(Mod.follower_count < int(term[11:]))
        elif term.startswith("tag:"):
            filters.append(Mod.tags.ilike('% ' + term[4:] + ' %'))
            filters.append(Mod.tags.ilike(term[4:] + ' %'))
            filters.append(Mod.tags.ilike(term[4:]))
            filters.append(Mod.tags.ilike('% ' + term[4:]))
        else:
            filters.append(Mod.name.ilike('%' + term + '%'))
            filters.append(User.username.ilike('%' + term + '%'))
            filters.append(Mod.short_description.ilike('%' + term + '%'))

    query = query.filter(or_(*filters))
    if category != None and category != "":
        if isinstance(category, str):
                query = query.filter(Mod.category.has(Category.name == category))
        else:
            query = query.filter(Mod.category.has(Category.id == category))
    if filtering_by_game == True:
            query = query.filter(Mod.versions.any(ModVersion.ksp_version == game_filtering_by))
    query = query.filter(Mod.published == True)
    query = query.order_by(desc(Mod.follower_count)) # We'll do a more sophisticated narrowing down of this in a moment
    total = math.ceil(query.count() / limit)
    if page > total:
        page = total
    if page < 1:
        page = 1
    results = sorted(query.all(), key=lambda r: weigh_result(r, terms), reverse=True)
    return results[(page - 1) * limit:page * limit], total

def search_users(text, page):
    terms = text.split(' ')
    query = db.query(User)
    filters = list()
    for term in terms:
        filters.append(User.username.ilike('%' + term + '%'))
        filters.append(User.description.ilike('%' + term + '%'))
        filters.append(User.forumUsername.ilike('%' + term + '%'))
        filters.append(User.ircNick.ilike('%' + term + '%'))
        filters.append(User.twitterUsername.ilike('%' + term + '%'))
        filters.append(User.redditUsername.ilike('%' + term + '%'))
    query = query.filter(or_(*filters))
    query = query.filter(User.public == True)
    query = query.order_by(User.username)
    query = query.limit(100)
    results = query.all()
    return results[page * 10:page * 10 + 10]

def typeahead_mods(text):
    query = db.query(Mod)
    filters = list()
    filters.append(Mod.name.ilike('%' + text + '%'))
    query = query.filter(or_(*filters))
    query = query.filter(Mod.published == True)
    query = query.order_by(desc(Mod.follower_count)) # We'll do a more sophisticated narrowing down of this in a moment
    results = sorted(query.all(), key=lambda r: weigh_result(r, text.split(' ')), reverse=True)
    return results

def search_users(text, page):
    terms = text.split(' ')
    query = db.query(User)
    filters = list()
    for term in terms:
        filters.append(User.username.ilike('%' + term + '%'))
        filters.append(User.description.ilike('%' + term + '%'))
        filters.append(User.forumUsername.ilike('%' + term + '%'))
        filters.append(User.ircNick.ilike('%' + term + '%'))
        filters.append(User.twitterUsername.ilike('%' + term + '%'))
        filters.append(User.redditUsername.ilike('%' + term + '%'))
    query = query.filter(or_(*filters))
    query = query.filter(User.public == True)
    query = query.order_by(User.username)
    query = query.limit(100)
    results = query.all()
    return results[page * 10:page * 10 + 10]
