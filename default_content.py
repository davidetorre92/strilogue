"""Default content and examples"""

DEFAULT_ZDOOM_EXAMPLE = '''namespace = "ZDoom";

conversation
{
    actor = "ChaingunGuy";
    page //1
    {
         name = "Chaingun Guy";
         dialog = "I have a cool chaingun! I want a shotgun though...";
         choice
         {
             text = "Deal!";
             giveitem = "Chaingun";
             nextpage = 2;
             nomessage = "No shotgun, no chaingun!";
             cost
             {
                 item = "Shotgun";
                 amount = 1;
             }
         }
    }
    page //2
    {
         name = "Chaingun Guy";
         dialog = "I love this!";
    }
}'''

DEFAULT_PLAIN_TEXT_EXAMPLE = """#NAME Chaingun Guy
#Page 1
I have a cool chaingun! I want a shotgun though...
#CHOICE:
- Deal! (#give(Chaingun), #nextpage(2), #nomessage(No shotgun, no chaingun!))
---
#NAME Chaingun Guy
#Page 2
I love this!
#CHOICE:"""