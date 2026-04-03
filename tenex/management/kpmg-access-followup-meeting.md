I have all the right services that you potentially would need because it takes a little bit to set them all up and I don't want to have to go in afterwards and delay any kind of production that you guys are working on. One of the things I was kind of like rolling through here, I didn't see anything in here for any kind of like... Vectorized data. For a learning model that I think would potentially be required within this build.

I don't know for sure, but I just didn't know if you want to put something there, maybe use Cosmos or something like that for vectorized capabilities. I know that you do have Redis in there for Memcache. Um... So I just want to kind of raise those concerns if you thought about any of those kind of like, when you get the scope, could potentially lead to extensive modeling of the data.

Yeah, I think that's a good call out. I think we'll definitely need some type of vector DB provider. If we have Postgres provisioned, we could use PG vector, but I think that Volume of data we'll be dealing with probably warrants standalone vector DB, so definitely a good call out.

Yeah, can you send me back like what flavor you guys prefer? I don't want to select for you because I don't know what the team, you know, every team has their own flavor they enjoy best, right?

Yeah, sounds good. I'll make note of that.

And then there is going to be probably API configurations, MCP configurations. I'm going to look to see about the security between two different systems that might be communicating with each other. I didn't know if you guys had any ideas on how you want to deal with any kind of like API gateways or anything else too within that sector. So for consideration within data communication. I doubt there's going to be any real-time data situations.

for an mvp but you know just in consideration of communicating with outside services um I didn't see anything in here in provision of that as well either.

Yeah, yeah. So I guess. I think we should definitely provision that to Question for you, should we be more like overly liberal with the amount of things we're asking to provision just to be kind of cautious so we don't have to circle back for access?

Yeah, for me, it's easier to turn off a service than it is to request to get one turned on. So always ask for more and then we can go from there, right?

Okay, that makes a lot of sense.

And I feel bad because I know you guys don't have a full scope and a few full, but I always like to prepare. As I always tell everyone on my teams that, you know, you always plan for the worst case scenario and hope for the best. Yep. Yeah, definitely.

Okay, so,All right, yeah. Um... Making note of all those things, and I'll do a second pass and just kind of add anything that we predict we might need, even if we don't know we'll definitely need. But did you have any other call outs from that list that you noticed?

Well, you know, I'm kind of concentrating more on the AI configurations of things and, of course, communications. You know, personally, I prefer an MCP connection rather than an API connection. I know that from my look from the API documents from the vendor, they have both available to you. So, but I'm not a part of the build, so I want to make sure that you have those options and you have those capabilities.

My suggestions in it, like I said, is, Have your imagination open, request more services. And like I said, I can reduce services as needed as we go through it and expect a lot of modeling inside of it because they do expect a lot of intelligence on the MPP. Okay.

All right, that's good to know. And yeah, in terms of MCP versus API, I think we probably just want both provisions that we can Yeah, they're both available.

I just need to make sure too that we have a pass-through that is good for you and you don't have to do a lot of extra coding just because the pass-through is too strict. Okay. All right, that sounds good.

And is this... Are these configurations for a specific third party provider or? Is this just general access within Azure?

This MVP probably could be for multiple different providers in the future and stuff. I think I don't know what the test would all encounter. I just like to keep things more generalistic. We don't know yet, but we should make sure that it can communicate easily, right? Yeah, absolutely. And I hope Andrew And as you want to chime in on anything, I don't know the vendors. I know there's a lot of talk of many different vendors potentially that can be tested within the environment.

So. I think right now it's just gonna be Rilla and Stute.

Okay. Yeah, that's the other thing I'd flag on my end, I guess. That's kind of the answer for what we're starting with, but I don't feel like I have a good map quite yet of any third-party... Vendors that we'd be integrating with so Um. But I guess if it's Rillett Institute to begin with, that's all we need.

Yeah, it'd be those two guys. Cool. I did get an API document from Relit. I'll send you over a link. Before that, It looks mainly SDK. So basically it will respond to you as you need data. So I'll send it over to you. So if it may help you also determine if you need anything extra from the services from the development environment that we're putting it on. Okay. Yep. That sounds great. Do you have any other questions?

Concerns? I was just going to roll it back to Brett and I'll get more talk to you.

Dan, do you have anything for me thatNo, I think my next action item from this is just gonna be to go through and try to anticipate anything that we might need and kind of like go through all that documentation It's going to be a little more predictive. I think my first pass at this was just sort of the baseline things I know we'll definitely need. So yeah, I'll get back to you very shortly with all that.

Okay. Yeah. Awesome. Perfect. Sounds good. Adam, do we want to pivot to logistics for the sessions? Anything else first? Cool. As far as logistics, so I think on the, so I think we aligned on the, For the 24th, we would do the full day working session. Yeah. Yeah. And I think one flag Arman is still going to be at the, he'll still have the doctor's appointment, but he may show up like just like an hour or so late Andrew.

So I don't know if he mentioned that to you directly or not. Okay. Great. Perfect. So yeah, I mean, Adam, I think as far as that, let's, I can work with you maybe offline to just align on like the attendees so that we can get the invites sent out. I think, And correct me if I'm wrong, but I think we spoke about doing both sessions at our office, or did we want to do one session at yours, one at ours?

So just so you guys know, You can't come to a KPMG office without us getting security clearance and all this other crazy stuff.

So it was much easier to just say 10X will never be on-site working with KPMG. No problem. Yeah, definitely hear that. No, Olga, just wanted to throw that out there. But yeah, no, we're happy to host. So we can do both days. We'll reserve some conference rooms on our end for the logistics. But then, Adam, would it make sense for us to just put out a hold for 10X? days so that we just make sure everyone's calendar is locked down.

Yeah, I sent one out to my team internally to everyone who has to be there. And then I could send it out to you guys as well. Why doesn't Brett send it out? You give him the names and emails just because then he can put in the logistics information. Yeah. They have it going like back and forth between the two of you.

Perfect. Yeah, so I'll, so yeah, Adam, if you don't mind just getting me those attendees for the 24th and then the April date, I can put the, those invites together and then I'll invite the folks from our side that will be joining.

And then We have a pretty good idea of what we want to cover for the morning session from our side. And I think, Am, you've shared that, right? I haven't sent it in writing yet. Okay. I can do that after this. We can go over right now if you want. We can do both. We would like to see what you guys want to cover in the afternoon session, just because we want to make sure if there's any other topics we want to get in there, we do.

And then we'll work together on the April 7th session agenda. Perfect. Sounds good. Yeah. Adam, did you want to pull it up now or did you want to send it offline? Because we can probably react to it and then just pull it together.

Yeah, it's not super. I can go over it quickly. So day one would be morning session led by us. So it would just be the overall vision of Pascal, which is the idea. Goals for the three-month sprint that we have. Any key challenges on what you guys would need to solve. And then we have like our prototype. So we do like a walkthrough of the current prototype we have. And then the afternoon would be led by you guys, which they'll drop the agenda for that.

And then we'll have like a 10 day working period until the until the 7th. And then our assumption to be there would be a lot of follow-up questions for scoping. And then you guys will develop your execution plan and then submit an order form to us. And then on the 7th, You guys will present how I will accomplish this.

Yeah, I think that makes sense. And we'll, I think we'll come into the seventh right with with agenda prepared just based on like our findings and I think some of the outcomes from the 24th session. So we'll put that together. But yeah, Adam, you'll send over the agenda.

Send it over and then you fill out.

Yeah, and then we'll align internally on some of the topics that we want to cover for the day. for our end. Cool. I'm just trying to think, is there, so we have the attendees. Place lockdown, agenda, anything else for those two sessions we're forgetting? I'll be Paula. And then we'll cater lunch, breakfast, coffee, everything like that. Oh, yeah. Sorry, I hadn't even thought about that. Any dietary restrictions that we should be aware of?

We'll try to have gluten-free options, vegan, but anything... Um, Not like in those categories that we should be aware of.

I'm kosher, but you don't have to cater towards that.

It's all good. We'll get a kosher option.

No, no, you don't need it. I don't want to be that guy. Perfect. I can eat, I can pretty much eat anything.

And just so, and just on the attendee side, by the way, Roughly how many people on your side do you think for the 24th and the 7th?

I think it's...

It's probably gonna be is Probably five or six. Five. And everyone will be in person? Four.

Should be set. Okay.

Okay, cool. So we'll earmark around like seven, eight, all in person right now and join you remotely. We'll have some people join remotely. Perfect. Sounds good. Cool. All right, I think we got that covered.

Anything else not-So why don't we go over the preliminary scope? So the reason why we haven't shared it yet is next week we're meeting with the first pilot customer to just finalize things. We're aligning with RILIT because they're essentially adopting RILIT as their new ERP. And then RILIT's being integrated into PESCALE. Dan, I don't know. I feel like I've met you before on one of our calls when we talked about...

Okay. Yeah. Adam, can you kind of walk through that preliminary scope? Yeah, let me pull it up. Actually, I sent it to Devin too, so I have it handy. Okay. So... Oh, go ahead. You got it? No, no, no. I don't have it. You go ahead. So basically, part of this is stuff that we also have to do, we'll need your help on, is the AI-native architecture and the foundation for the platform, right? a data model that is aligned to the current digital finances data model.

We're not going to be able to Institute Integrations. And then... I think this is also going to be something that David talks a lot about as a CFO agent. Because it's going to have to have like a high level of accuracy, right? Because it's finance. A fully automated 13-week cash flow. And some of this will come to life when they start showing you the prototype on the 24th. There will be a dashboard that has like a CFO level view of everything that's happening from a financial perspective.

And that should be direct... tied directly to the financial data that's coming in from RILA and that is being like processed through PESCALE. It should enable users to ask questions and get like... Hi. Highly correct answers. Right. From the CFO agent, like in phase one, we'll also focus on questions where it can ask about the 13 week cash flow. Highlight stressors like variances, um, And then we'll get more detail here because that's what we're doing on Wednesday with the design partner about like, what are these sort of blind spots the CFO needs help with that this agent needs to surface?

Yeah, that's the big stuff.

I think that makes sense. Yeah, I think that makes sense to us too.

Yeah, and we'll definitely, Adam or Andrew, if you guys have a document, we'd love to take a look at that as well.

We can pass it around to Armand and just see if he's got his opinion on it as well. Perfect. Great. Anything else we should discuss or just leading into some of these sessions? Anything you guys need from us?

I don't think so right now. I'm sure something will come up.

a list of some of the technical requirements and tools. And then Adam or I will be sending the invite. You'll be sending the attendees from your side. We'll work out the logistics. And then I think Andrew or Adam, you guys will send the... the scope materials. Anything else that that we discussed that...

Yeah, I'll send it over to the tenant as well and then just send it back with your input in it. Okay. Who's going to be the technical contact from this point forward with TEDx?

I think that will be Dan. So you can coordinate with Dan on anything from a technical side. Dan leads our engineering.

Well, one thing I'd like to do at some point in time, Dan, is introduce you to Relent so that you guys can communicate directly with each other, especially if there's API communication issues or anything else while you're developing. So I'm going to find out their technical contact and kind of share information that way. Good call. Yeah, that's a great call. you Sounds good. Cool.

All right. Sounds good. Well, it's a Friday. Hope you guys have a great weekend. If there's anything else that we can do, we're a text, email way. Sounds good, guys. All right. Thank you. And Dan, go crazy on your wish list because you better have more than not enough, right? Oh, if you tell that to Dan, he'll go crazy. He'll go all out. It'll be like five. I'd rather deal with that than the opposite, right? All right. Thanks, everyone. Bye.