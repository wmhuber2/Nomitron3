Bot Commands:

    !rule $num        :
    !r $num           :  Display Rule Number $num if it exists.

    !find KEY_WORDS   :
    !search KEY_WORDS :
    !f KEY_WORDS      :  Display rules that contain text.

    !help             :  Display This Help Text
    !roll [[d]]#      :  Roll dice

    !challenge        :  Challenge a gladiator

    !give @player               : Give @player a Friendship Token
    !offer @player #NUM [TERMS] : Create an offer in #market
    !offer #NUM [TERMS]         : Create an offer in #market

    !green            :  Turn Green
    !orange           :  Turn Orange
    !purple           :  Turn Purple

    !ping             :  Pings Bot
    !turnStats        :  Get Turn Debug Info

    !me               :  Get Your Player Info

Mod Commands:

    !sudo             :  Add Mod Role
    !sudont           :  Removes Mod Role

    !clear            :  Clear Current Channel
    !clearAll         :  Reset Bot Completeley (Blocked)

    !restart          :  Restart Bot
    !uploadData       :  Upload Bot YAML Data File


    !popProposal      :  Put top proposal on Queue in Voting
    !setProp $num     :  Set proposal Number to $num
    !enableVoting     :  Enable voting 
    !removeProposal $player
                      :  Remove $player's propsal from Queue


    !extendTurn       :  Extend current turn by 24 hrs
    !reduceTurn       :  Reduce current turn by 24 hrs
    !tickTurn         :  Start next turn


    !green @player    :  Turn @player Green
    !orange @player   :  Turn @player Orange
    !purple @player   :  Turn @player Purple

    !resetChallenges         :  Reset Tracker for "if player has challenged" for all players
    !resetChallenges @player :  Reset Tracker for if player has challenged for @players
    !setGladiator @player    :  Set the player as Gladiator

    !setTokens @player NUM   : Set player's frinedship tokens to NUM
    !setOffer @player NUM    : Set player's offered frinedship tokens to NUM