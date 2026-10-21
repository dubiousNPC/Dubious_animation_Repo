### **Dubious animation Repo**
------------------------------


 Free open source library of hand made animations made for Morrowind with the OpenMW engine in mind.
 I make animations in blender for fun and this is where i keep them when they are mostly finished,
 list is not currently up to date with all animations added, as it is still in a state up updating
 Think of it as an open Beta, there is a good chance that everything here will get another polish pass at some point
 
 everything here is available for use under CCO license. use, share and enjoy. Be Excellent to each other
  
**proper documentation can be found here**
--------------------------------------------------
https://openmw.readthedocs.io/en/latest/reference/lua-scripting/openmw_animation.html
--------------------------------------------------
    
     
      
**A bog-standard note on animation**
 
I am not skilled in coding but here is very basic example of animating in OpenMW:  
  
animations are split up by Text Keys in the KeyFrame data. in the .kf files like [xpetit.kf], text keys are listed in "NiTextKeyExtraData", essentially these are markers in the animation that you can call with your script.

so e.g. you will see "petit: start" and "petit: stop"

so you can call to the groupname "petit" and play a loop from "start" to "stop" and it will loop the animation between those two points.

for example:

----------------------------------------------------------------------
local I = require("openmw.interfaces")
local anim = require("openmw.animation")

local function onScribPetted()
    I.AnimationController.playBlendedAnimation(
        "petit",
        {
            startKey = 'start',
            stopKey = 'stop',
            priority = {
                [anim.BONE_GROUP.LeftArm] = anim.PRIORITY.Scripted,
                [anim.BONE_GROUP.Torso] = anim.PRIORITY.Scripted,
            },
            autoDisable = true,
            blendMask = anim.BLEND_MASK.LeftArm + anim.BLEND_MASK.Torso + anim.BLEND_MASK.RightArm +
            anim.BLEND_MASK.LowerBody,
            speed = 1
        }
    )
end

return {
    eventHandlers = {
        PetTheScribs_ScribPetted = onScribPetted,
    }
}
----------------------------------------------------------------------
check out the excellent mod that allows for such glorious action
https://www.nexusmods.com/morrowind/mods/58294
  
  
   
In another example using "iajutsheathe2" as a weapon attack you would then need to attach the weapon to the Weapon Bone and use the Text Keys for "discard" that can be called to sheathe the weapon. could maybe do something like this:

----------------------------------------------------------------------
        anim.addVfx(self, 'meshes/w/w_n_katana', {
            loop = true,
            vfxId = "iajutsublade",
            boneName = "Weapon Bone",
        })    
 
        I.AnimationController.addTextKeyHandler('sheathe', function(groupname, key)
            if key == 'discard' then
                anim.removeVfx(self, iajutsublade)
            end
        end)
end
----------------------------------------------------------------------
so then it would autmatically pull a katana out of nowhere and sheathe it again.
like i said i'm no coder. credit to MrArrean on OpenMW Discord for showing me this simple method.
there's lots of ways to approach it.



## ANIMATIONS
--------------

# xbugmusk:   
3rdP 3-second dousing animation. 2 variants    
<ins>Alternate files bugmuskROTbone:</ins> **experimental** weapon bone rotated 90 degrees

**KEYS**    
<ins>bugmusk1:</ins> *start/stop*   
<ins>bugmusk2:</ins> *start/stop*   



https://github.com/user-attachments/assets/5d51b654-21e0-4b18-ac02-2ff003fe62b0



# xdisarm:   
1st/3rd 1-second disarmed reaction. 3 variants

**KEYS**    
<ins>disarm1:</ins> *start/stop*   
<ins>disarm2:</ins> *start/stop*   
<ins>disarm3:</ins> *start/stop*   

https://github.com/user-attachments/assets/0ec10f00-5673-47ff-8b1d-cec8c3a360e0


https://github.com/user-attachments/assets/2d9e0304-a0db-4eda-8b6b-18f137c12341


# xdrinking:   
standing around drinking

**KEYS**    
<ins>drink1:</ins> *start/discard/stop*   
<ins>drink2idle:</ins> *start/stop*   
<ins>drink2:</ins> *start/stop*   
<ins>drink3idle:</ins> *start/stop*   
<ins>drink3:</ins> *start/stop*   
<ins>drink4idle:</ins> *start/stop*    
<ins>drink4:</ins> *start/stop*    



https://github.com/user-attachments/assets/3e0b0037-1cab-4682-8885-8e2b278e4321

# xeating:   
1st/3rd 3-second eating by hand or from a soup bowl. left hand and torso

**KEYS**    
<ins>eatingr:</ins> *start/stop*   
<ins>eatingl:</ins> *start/stop*   
<ins>eating2:</ins> *start/stop*   



https://github.com/user-attachments/assets/5ce6c540-a39a-49cb-834b-524d84fba504



# xEmotes1:

3rd person emotive gestures



https://github.com/user-attachments/assets/903afbf8-92cb-4ad0-83e3-02e00bf8e17c



https://github.com/user-attachments/assets/c3f545ef-73ba-435c-9542-faf0212f4705







# xfollow:   
1st/3rd 1-second beckon and wait gestures. left hand and torso

**KEYS**    
<ins>followme:</ins> *start/release/stop*   
<ins>wait:</ins> *start/release/stop*   


https://github.com/user-attachments/assets/62a30484-8f8b-4ab3-8cdf-f34b4968769c



# xForceThrow:   
3rd force choke/telekenesis

**KEYS**   
<ins>fchokeidle:</ins> *start/loop start/loop stop/stop*    
<ins>fchokefly:</ins> *start/loop start/loop stop/stop*   
<ins>fchokedrop:</ins> *start/loop start/loop stop/stop*   
<ins>fchokeend:</ins> *start/stop*   
<ins>fchoke1:</ins> *start/loop start/loop stop/stop*   
<ins>fchoker:</ins> *start/stop*   
<ins>fchokel:</ins> *start/stop*   
<ins>fchokefwd:</ins> *start/stop*  
<ins>fchoketwd:</ins> *start/stop*  



https://github.com/user-attachments/assets/432f78b5-c623-4d6a-a358-2e8a467e558e





https://github.com/user-attachments/assets/38022201-fed5-45e2-ad76-2ffe0c324654





# xhookshot:   
1st/3rd aim and firing arm-mounted grapple hook

**KEYS**   
<ins>hookaim:</ins> *start/loop start/loop stop/stop*    
<ins>hookgo:</ins> *start/loop start/loop stop/stop*   
<ins>hookhang:</ins> *start/stop*   
<ins>hookhangup:</ins> *start/loop start/loop stop/stop*   
<ins>hookhangdwn:</ins> *start/loop start/loop stop/stop*   


https://github.com/user-attachments/assets/30a1ad58-5618-4cbf-9bbd-6ae3cc076c67


# xIajutsu:   
3rd iajutsu style pose and strike. not combat ready

**KEYS**    
<ins>iajutsuprep:</ins> *start/stop*   
<ins>iajutsucon:</ins> *start/stop*
<ins>iajutsuslice:</ins> *start/stop*     
<ins>iajutsusheathe:</ins> *start/discard/stop*  
<ins>iajutsusheathe:</ins> *start/discard/stop*  



https://github.com/user-attachments/assets/f4065894-bc7f-4780-8dc0-0266d9a933ec




# xinteracting:   
3rdP 1-second object interaction animation. right handed. 4 variants    

**KEYS**    
<ins>loot1:</ins> *start/attach/stop*   
<ins>loot2:</ins> *start/attach/stop*    
<ins>loot1:</ins> *start/discard/stop*   
<ins>loot2:</ins> *start/discard/stop*    


https://github.com/user-attachments/assets/3b11e3ae-9739-4a0a-b7f7-91aa6d6fd1de



https://github.com/user-attachments/assets/5079e1b6-bdea-4045-8743-b19e8d6c07a7




# xknock:   
1st/3rd door knocking for left or right hand   

**KEYS**    
<ins>knockl:</ins> *start/stop*    
<ins>knockr:</ins> *start/stop*    
<ins>SoundGen:</ins> *left/right*    



# xmissdodge:   
3rd Person animations for dodging missed attacks, 8 directions   

**KEYS**   
<ins>missdr:</ins> *start/stop*   
<ins>missdl:</ins> *start/stop*   
<ins>missdfwd:</ins> *start/stop*   
<ins>missdbk:</ins> *start/stop*   
<ins>missdfwdr:</ins> *start/stop*   
<ins>missdfwdl:</ins> *start/stop*   
<ins>missdbkr:</ins> *start/stop*   
<ins>missdbkl:</ins> *start/stop*   


https://github.com/user-attachments/assets/b6237fde-258c-4f10-8c6a-d3bd946ecc2d

# xpotion:   
1st/3rd 2-second potion drinking

**KEYS**    
<ins>potion:</ins> *start/discard/stop*     


# xprayer:   
1st/3rd praying anims for looping idles

**KEYS**   
<ins>prayer1:</ins> *start/loop start/loop stop/stop*    
<ins>prayer2:</ins> *start/loop start/loop stop/stop*   


https://github.com/user-attachments/assets/51bc8bd8-cd60-4955-9ba3-4cf0a8e53a21






# xRASitting1:   
 
1st/3rd praying anims for looping idles

**KEYS**   
<ins>rasit1:</ins> *start/stop*    
<ins>rasit1:</ins> *start/stop*    
<ins>rasit1:</ins> *start/stop*    
<ins>rasit1:</ins> *start/stop*    
<ins>rasit1:</ins> *start/stop*    
<ins>rasit1:</ins> *start/stop*    
<ins>rasit1:</ins> *start/stop*    
<ins>rasit1:</ins> *start/stop*    
<ins>rasitf:</ins> *start/stop*   
<ins>rasitf1:</ins> *start/stop*   
<ins>rasitf2:</ins> *start/stop*   


https://github.com/user-attachments/assets/969b9e59-13c6-4a67-8cb3-90319ce378fa


https://github.com/user-attachments/assets/2babde9f-567e-4730-9cb1-1ea1d515bc55




# xsearchtorch:   
3rdP searching/scanning upper body only     

**KEYS**   
<ins>search1:</ins> *start/stop*   
<ins>search2:</ins> *start/stop*   
<ins>search3:</ins> *start/stop*    



https://github.com/user-attachments/assets/76007f1c-026c-484d-a2f3-4e8387a2c18f


# xsidestep1:   
1st/3rd .25 second step-dodge animations, 8_directions     

**KEYS**   
<ins>dodger:</ins> *start/stop*   
<ins>dodgel:</ins> *start/stop*   
<ins>dodgefwd:</ins> *start/stop*   
<ins>dodgebk:</ins> *start/stop*   
<ins>dodgefwdr:</ins> *start/stop*   
<ins>dodgefwdl:</ins> *start/stop*   
<ins>dodgebkr:</ins> *start/stop*   
<ins>dodgebkl:</ins> *start/stop*   



https://github.com/user-attachments/assets/1df793ae-58ea-43d8-a399-4b51d1de8bce


# xsitting:   
3rdP 8 sitting idles    

**KEYS**   
<ins>dbssit1:</ins> *start/stop*   
<ins>dbssit2:</ins> *start/stop*   
<ins>dbssit3:</ins> *start/stop*   
<ins>dbssit4:</ins> *start/stop*   
<ins>dbssit5:</ins> *start/stop*   
<ins>dbssit6:</ins> *start/stop*   
<ins>dbssit7:</ins> *start/stop*   
<ins>dbssit8:</ins> *start/stop*     


https://github.com/user-attachments/assets/9d9c0aa9-b328-4109-b266-132f27c91b9c

# xsitting2:   
3rdP 8 sitting/resting idles with chair adjusting/transition anims   

**KEYS**   
<ins>chairmove1:</ins> *start/stop*   
<ins>chairmove2:</ins> *start/stop*   
<ins>rmanuv:</ins> *start/stop*     
<ins>dbssit21:</ins> *start/loop start/loop stop/stop*    
<ins>dbssit22:</ins> *start/loop start/loop stop/stop*     
<ins>dbssit23:</ins> *start/loop start/loop stop/stop*   
<ins>dbssit24:</ins> *start/loop start/loop stop/stop*    
<ins>dbssit25:</ins> *start/loop start/loop stop/stop*    



https://github.com/user-attachments/assets/2479b14c-5bce-4456-bdd4-839cab95e6fe



https://github.com/user-attachments/assets/93d5afcb-bce5-4aa0-b7ab-54922e1e7186



https://github.com/user-attachments/assets/4c9b640c-a845-42de-810c-1f524c900c4f



# xsleept



https://github.com/user-attachments/assets/f55221a9-9736-4a5f-bfe1-6a6270951ea5





# xsmoking:   
3rd 1-second pipe and cigar smoking

**KEYS**    
<ins>smoke1r:</ins> *start/stop*   
<ins>smoke1l:</ins> *start/stop*   
<ins>smokelight:</ins> *start/attach/stop*   
<ins>smokash:</ins> *start/stop*   
<ins>smoke2:</ins> *start/stop*   
<ins>smoke3:</ins> *start/stop*   
<ins>smokeflick:</ins> *start/discard/stop*   
<ins>smoke1ridle:</ins> *start/stop*   
<ins>smokepipe1:</ins> *stop/loop start/loop start/stop*   
<ins>smokepipe2:</ins> *start/stop*   
<ins>smoke5:</ins> *start/discard/stop*   

https://github.com/user-attachments/assets/f17e8d77-6a0e-48e2-97fc-f7c2ca3a9ae8






# xthumbs:   
3rdP 2 second thumbs up/thumbs down     

**KEYS**   
<ins>thumbs1:</ins> *start/release/stop*   
<ins>thumbs2:</ins> *start/release/stop*  


https://github.com/user-attachments/assets/77a64ada-4969-46ce-b500-eadb6255fce2




-----------------------------------------
## SOME MODS CONTAINING THESE ANIMATIONS
------------------------------------------
Smoking NPCs (OpenMW)  https://www.nexusmods.com/morrowind/mods/60477

Daily Chores   https://www.nexusmods.com/morrowind/mods/60161
  
NPC Personality - (Dynamic gestures - Faction Reactions)  https://www.nexusmods.com/morrowind/mods/60121
 
N'garde   https://www.nexusmods.com/morrowind/mods/58658

Can't touch this  https://www.nexusmods.com/morrowind/mods/59155

Pet the Scribs   https://www.nexusmods.com/morrowind/mods/58294

Follower Commands   https://www.nexusmods.com/morrowind/mods/58818

Devilish Knocking   https://www.nexusmods.com/morrowind/mods/59672
  
Evening Star - Faiths of Morrowind   https://www.nexusmods.com/morrowind/mods/59173?tab=description
  
Interactions Animated  https://www.nexusmods.com/morrowind/mods/59117
   
Consuming Animated   https://www.nexusmods.com/morrowind/mods/59069
   
Eating Habits    https://www.nexusmods.com/morrowind/mods/59350
   
Lua Bounty Hunter   https://www.nexusmods.com/morrowind/mods/58850
   
Lua Beast Tamer   https://www.nexusmods.com/morrowind/mods/59054
   
Praying Animated   https://www.nexusmods.com/morrowind/mods/59182
   
Disarm 'Em All   https://www.nexusmods.com/morrowind/mods/58430
    
Vaults Restricted   https://www.nexusmods.com/morrowind/mods/58405

Iaijutsu    https://www.nexusmods.com/morrowind/mods/59717



If you appreciate my work fell free to leave a donation with ko-fi   https://ko-fi.com/dubiousnpc

:D












