VAMP RACES PUMP.FUN - lancements du 22/10/2026 13:00 au 23/10/2026 13:00 UTC
Aucun appel RPC Solana, aucun enrichissement de metadonnees (pas d'IPFS, pas de telechargement d'images).

SOURCES (lecture seule)
- Lancements, curve sur les 15 premieres minutes (tx, SOL, tx suspicious exclues), statut de graduation :
  donnees deja collectees (snapshot on-chain du 23/10 14:22 UTC, heure de graduation = dernier trade curve).
- Nom / ticker / image_uri : circular.tokens + circular_realtime.tokens (deja en base).
- Volumes 2 min / 1 h / 24 h / a date : circular.prices (source onchain, suspicious = 0, USD, toutes plateformes),
  cutoff 23/10 15:15 UTC. Volume curve = avant l'heure de graduation, post-graduation = apres.

DEFINITION D'UNE RACE (race_id, fenetre principale 30 min)
- meme ticker normalise (majuscules, sans $, accents, espaces ni emojis) ;
- nom identique, contenu dans l'autre (>= 4 caracteres) ou similaire (ratio difflib >= 0,8), OU meme image (meme CID IPFS / meme URL) ;
- lance dans les 30 min qui suivent le premier lancement de la race.
- Sensibilite : race_id_w10 (10 min) et race_id_w60 (60 min).
- Exclus : 629 tokens qui tradaient > 2 min avant leur detection (pas nouveaux) et 10 tokens sans nom ni ticker en base.

ROLES / RANGS (fenetres propres a chaque token, a partir de son premier trade)
- leader_2m : plus gros volume sur ses 2 premieres minutes.
- winner_1h / winner_24h : plus gros volume sur sa premiere heure / ses 24 premieres heures.
- winner_24h seulement si les 24 h de TOUS les membres existent (lances avant 22/10 15:15 UTC) ; sinon vide + flag h24_incomplete.
- winner_to_date : provisoire (historique jusqu'au cutoff). winner_after_2m : plus gros volume entre la minute 2 et la minute 60.
- competitor : membre sans role (perdant).

DONNEES MANQUANTES / LIMITES (flags)
- Wallet createur non conserve : impossible de distinguer un relaunch du meme createur d'une vraie vamp.
- Images : 63 % des tokens sans image_uri en base ; URLs propres a chaque launcher -> seuls les CID/URL identiques sont reconnus ;
  aucune similarite visuelle calculee.
- Graduation figee au snapshot du 23/10 14:22 UTC : une graduation posterieure n'est pas vue (son volume post-graduation compte comme curve).
- Colonnes tx_* : 15 premieres minutes seulement.
- edge_of_24h_window_members_may_be_missing : race ancree a moins de 30 min du debut/fin de la fenetre.
- extreme_curve_volume_1h_possible_volume_bot : > 500 k$ sur la curve en 1 h sans graduer (probables bots de volume, non verifie apres 15 min).
- one_or_zero_active_members : 0 ou 1 membre avec >= 1 000 $ de volume en 1 h (copies mortes).
- tie_for_2m_leader, loose_name_match, no_2m_volume, prices_start_after_first_curve_trade, suspicious_tx_share_gt_20pct.

FORMAT : CSV UTF-8, separateur ';', decimales a virgule, horodatages UTC, booleens 1/0, volumes en USD arrondis.
FICHIERS : races.csv (1 ligne par race), race_members.csv (tous les membres, perdants inclus, tries par race puis rang 1 h),
all_mints.csv (les 18 075 tokens ; race_id vide = pas de race, excluded_reason = exclu).
