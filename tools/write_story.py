# Hand-curated story layer for the pilot. Every lineage edge carries evidence and a source.
# confidence: "sourced" = stated in cited text; "observed" = Claude's reading of the plot; "claude-knowledge" = needs checking
from common import *
WPU=lambda t:"https://en.wikipedia.org/wiki/"+t.replace(" ","_")
D={
"1922-nosferatu":dict(
 archetypes=[("The One Who Feeds","primary"),("The Contagion","secondary"),("You Invited It In","secondary")],
 motifs=[("vessel bringing death (ship)","observed","the vampire arrives by ship and the plague follows"),("plague and rats","sourced","plot: town blames plague"),("threshold and the house opposite","observed","Orlok buys the derelict house across from Hutter's"),("the woman who sacrifices herself","observed","Ellen keeps Orlok until dawn"),("forbidden book","sourced","Hutter takes a book about vampires from the inn"),("portrait of the beloved","sourced","Orlok admires Ellen's portrait")],
 lineage=[("adapted_from","Dracula (Bram Stoker, 1897)","sourced","an unofficial and unauthorized adaptation of Bram Stoker's 1897 novel Dracula",WPU("Nosferatu")),
          ("legend","Eastern European vampire folklore (strigoi, nosferatu)","claude-knowledge","folk vampire tradition behind Stoker's novel","")]),
"1960-psycho":dict(
 archetypes=[("The Devouring Mother","primary"),("The Double","secondary"),("The Bad Host","secondary")],
 motifs=[("the motel as trap (bad host)","sourced","rainstorm forces Marion to stop at the secluded Bates Motel"),("mother in the house on the hill","sourced","Norman argues with his mother"),("water / drowning the evidence","sourced","sinks the vehicle in a swamp"),("taxidermy, the preserved dead","sourced","his hobby as a taxidermist"),("stolen money","sourced","embezzles $40,000")],
 lineage=[("adapted_from","Psycho (Robert Bloch, 1959)","sourced","based on the 1959 novel by Robert Bloch",WPU("Psycho (1960 film)")),
          ("inspired_by_real","Ed Gein case (Wisconsin, 1957)","sourced","loosely inspired by the case of convicted Wisconsin murderer and grave robber Ed Gein",WPU("Psycho (1960 film)"))]),
"1973-the-exorcist":dict(
 archetypes=[("The Voice Inside","primary"),("You Invited It In","secondary"),("The Devouring Mother","tertiary: the priest's guilt over his mother")],
 motifs=[("spirit board / invitation","sourced","Regan discovers a spirit board and contacts 'Captain Howdy'"),("ancient idol unearthed","sourced","Merrin finds a talisman of a winged being in Hatra"),("the child's voice replaced","sourced","speaks in an otherworldly voice"),("guilt toward a dead mother","sourced","Karras guilty at not having been with his mother when she died"),("the stairs / the fall","sourced","Dennings found dead at the bottom of public stairs")],
 lineage=[("adapted_from","The Exorcist (William Peter Blatty, 1971)","sourced","novel source",WPU("The Exorcist (novel)")),
          ("inspired_by_real","Exorcism of Roland Doe (1949)","sourced","The novel was inspired by a 1949 case of supposed demonic possession and exorcism",WPU("The Exorcist (novel)")),
          ("legend","Pazuzu (Assyrian and Babylonian demon)","claude-knowledge","the winged statue in the prologue","")]),
"1998-ringu":dict(
 archetypes=[("The Woman Who Comes Back","primary"),("The Thing You Took Home","secondary"),("The Rule","secondary: seven days")],
 motifs=[("woman thrown into a well","sourced","Dr. Ikuma trapped Sadako inside the well"),("long black hair, white dress","sourced","dressed in a simple white dress usually with long black hair hiding her face (Sadako Yamamura article)"),("cursed media","sourced","a videotape that curses its viewers to die in seven days"),("the copy that spreads the curse","sourced","copy of the tape"),("psychic mother","sourced","Shizuko's public demonstration of psychic ability")],
 lineage=[("adapted_from","Ring (Koji Suzuki, 1991)","sourced","novel source",WPU("Ring (Suzuki novel)")),
          ("inspired_by_real","Sadako Takahashi, early-20th-century psychic","sourced","Sadako is also based on the life of early-20th century psychic Sadako Takahashi",WPU("Sadako Yamamura")),
          ("shares_motif","Okiku, Banchō Sarayashiki (1741)","observed","both are women murdered and thrown into a well who return; no direct influence is claimed in the sources read",WPU("Banchō Sarayashiki")),
          ("remade_as","The Ring (2002) and The Ring Virus (1999)","sourced","Korean and American films reimagine the character",WPU("Sadako Yamamura"))]),
"2004-pontianak-harum-sundal-malam":dict(
 archetypes=[("The Woman Who Comes Back","primary"),("The Inherited Curse","secondary: the past returns 50 years later")],
 motifs=[("woman who dies pregnant returns","sourced","Meriam is later discovered dead while pregnant"),("scent of the tuberose (sundal malam)","sourced","English title: Pontianak Scent of the Tuber Rose"),("two eras, one face","sourced","Maria bears an uncanny resemblance to Meriam"),("the performer (gamelan prima donna)","sourced","gamelan prima donna Meriam"),("rivalry between suitors","sourced","torn between two men")],
 lineage=[("legend","Pontianak / Kuntilanak (Malay and Indonesian folklore)","sourced","a restless spirit (pontianak) Meriam who seeks revenge",WPU("Kuntilanak")),
          ("shares_motif","Sadako (Ringu)","observed","long-haired woman in white who returns for revenge",WPU("Kuntilanak"))]),
"2016-train-to-busan":dict(
 archetypes=[("The Contagion","primary"),("The Dead Won't Stay Dead","secondary"),("The Bad Host","tertiary: passengers who bar the door")],
 motifs=[("a dead deer rises","sourced","A deer is hit by a truck and reanimates"),("the sealed carriage / who gets let in","sourced","refuse to let them into their carriage and block the door"),("the selfish father redeemed","sourced","cynical workaholic and divorced father"),("pregnant woman protected","sourced","his pregnant wife Seong-kyeong"),("the vessel (train)","observed","the whole film runs on one train")],
 lineage=[("followed_by","Peninsula (2020)","sourced","standalone sequel",WPU("Train to Busan")),("prequel","Seoul Station (2016)","sourced","animated prequel",WPU("Train to Busan"))]),
"2017-get-out":dict(
 archetypes=[("The Bad Host","primary"),("The Double","secondary: bodies taken over"),("Nobody Believes Her","tertiary: Rod")],
 motifs=[("the family that welcomes you","sourced","meet the family of his white girlfriend"),("teacup and spoon (hypnosis)","sourced","the sound of a spoon stirring in a teacup"),("the sunken place","sourced","a dark void she dubs the sunken place"),("guilt toward a dead mother","sourced","his mother died in a hit-and-run when he was 11"),("a deer struck on the road","claude-knowledge","Rose hits a deer on the drive; not in the Wikipedia plot, check against the film"),("the auction","sourced","silent auction for a photo of him")],
 lineage=[]),
"2018-tumbbad":dict(
 archetypes=[("The Bargain","primary"),("The Hunger","secondary"),("The Inherited Curse","tertiary")],
 motifs=[("the goddess's womb (descent)","sourced","descends into the womb with a rope"),("gold from the hungry god","sourced","steals gold coins from Hastar's loincloth"),("starving grandmother in chains","sourced","a disfigured and starving old woman chained"),("dough doll as bait","sourced","lures Hastar with a flour dough doll"),("endless rain on a cursed village","sourced","cursed the village with incessant rain"),("father teaches son the trade","observed","greed passed down")],
 lineage=[("adapted_from","'Aaji' (Narayan Dharap), after Stephen King's 'Gramma'","sourced","a story, Aaji, by Marathi writer Narayan Dharap ... had based Aaji on King's short story Gramma",WPU("Tumbbad")),
          ("adapted_from","'Bali' (Narayan Dharap)","sourced","the film also partially derives from Bali, another Dharap short story",WPU("Tumbbad")),
          ("draws_on","Hastur (Cthulhu Mythos, via Dharap)","sourced","also featured Hastur from the Cthulhu Mythos",WPU("Tumbbad")),
          ("draws_on","Vikram and Betaal; Panchatantra","sourced","referenced by Barve",WPU("Tumbbad"))]),
"2018-hereditary":dict(
 archetypes=[("The Inherited Curse","primary"),("The Village Needs Blood","secondary: the coven"),("The Devouring Mother","secondary")],
 motifs=[("miniatures and dioramas (the house as model)","sourced","Miniatures artist Annie Graham"),("decapitation","sourced","Charlie is decapitated by a telephone pole"),("a deer on the road","sourced","Peter swerves to avoid a dead deer"),("séance / invitation","sourced","communicate with Charlie's spirit via séance"),("the grandmother's coven","sourced","Ellen as Queen Leigh, the leader of a coven"),("demon wants a male host","sourced","Paimon prefers to inhabit a male host")],
 lineage=[("draws_on","Paimon (Ars Goetia / The Lesser Key of Solomon)","sourced","The demon king Paimon originates from numerous grimoires, including The Lesser Key of Solomon",WPU("Hereditary (film)"))]),
"2019-la-llorona":dict(
 archetypes=[("The Woman Who Comes Back","primary"),("Nobody Believes Her","secondary: the testimonies dismissed"),("The House Remembers","tertiary: the besieged house")],
 motifs=[("weeping woman","sourced","The sound of a woman weeping"),("water and drowned children","sourced","Supernatural activity involving water ... Alma had a son and daughter who died"),("the maid who arrives","sourced","brings in a young woman named Alma to work as a maid"),("the house under siege","sourced","protests ... trapping the family in the house"),("history's crime returns","sourced","convicted for orchestrating the native Mayans's genocide")],
 lineage=[("legend","La Llorona (Mexican and Latin American folklore)","sourced","film reworks the legend",WPU("La Llorona")),
          ("inspired_by_real","Efraín Ríos Montt and the Guatemalan genocide","sourced","Enrique Monteverde (based on Efraín Ríos Montt)",WPU("La Llorona (2019 film)"))]),
}
for fid,v in D.items():
    rec={"film":fid,"archetypes":[{"name":a,"role":r,"status":"first pass, unreviewed"} for a,r in v["archetypes"]],
         "motifs":[{"motif":m,"confidence":c,"evidence":e} for m,c,e in v["motifs"]],
         "lineage":[{"relation":rel,"target":t,"confidence":c,"evidence":e,"source":s} for rel,t,c,e,s in v["lineage"]],
         "notes":"confidence: sourced = stated in the cited text; observed = Claude's reading of the plot; claude-knowledge = from Claude's own knowledge, verify before use",
         "updated":today()}
    json.dump(rec,open(f"{fdir(fid)}/story.json","w"),indent=1,ensure_ascii=False)
print("ok",len(D))
