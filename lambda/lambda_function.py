# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils


from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
import requests
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

gameid = ""
gamedata = {"level":1,"color":"white"}
class LaunchRequestHandler(AbstractRequestHandler):# this is for starting the chess game

    #starts through saying "voice chess"
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        
        speak_output = "testing"
        
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        # type: (HandlerInput) -> Response
        gamedata = {"level":1,"color":"white"}
        response=requests.get("https://lichess.org/api/account", headers={"Authorization": ""})
        responsetext = response.text
        a = json.loads(responsetext)
        username = (a["id"])
        speak_output = "Hi "+ username + " Welcome to Alexa voice chess, you would you like to play a game?"
        Challenge=requests.post("https://lichess.org/api/challenge/ai", headers={"Authorization": ""}, data = gamedata)
        ChallengeText = Challenge.text
        ChallengeJson = json.loads(ChallengeText)
        gameid = ChallengeJson["id"]
        session_attr["gameid"] = gameid
        
        session_attr["whitePeices"] = {"knight":["g1","b1"],"queen":"d1","rook":"h1","king" : "e1" }
        print(gameid)
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class ChessIntentHandler(AbstractRequestHandler):# this is for the constant back and forth between user and alexa
    def MoveMaker(move,session_attr,PieceName):
        gamedata = {"level":1,"color":"white"}
        response=requests.post("https://lichess.org/api/board/game/"+session_attr["gameid"]+"/move/"+move, headers={"Authorization": ""})
        speak_output = "Not set"
        if(response.status_code==400):
            if(PieceName != "pawn"):
                print("new square for knight is "+move)
                speak_output = "Moved Successfully"
            else:
                if(PieceName != "pawn"):
                    print(session_attr["whitePeices"][PieceName])
                speak_output = "Moved UnSuccessfully"
        return speak_output
        
    def knightHandler(RowDestination,ColumnDestination,session_attr):
        matchingknights = []
        Columns = ["a","b","c","d","e","f","g","h"]
        knights  = session_attr["whitePeices"]["knight"]
        print("desination is " + (ColumnDestination+RowDestination).lower())
        matchingknights = session_attr["whitePeices"]["knight"]
        matchingcount = 0
        for k in range(0,len(knights)):# this loops through both knights to check which/either of them can make the legal move.
            knight = knights[k]
            index = Columns.index(knight[0])
            print(knight)
            print("the index is"  + str(index))
            for i in range(index-2,index+3 ):# this gets the to previous columns and the two leading columns
                if(i > -1 and i <8):
                    if(i != index):
                        rowcount =abs(index - i)# if e then row count =  2
                        up = 3-rowcount
                        down = rowcount - 3
                        print("possible square is " +  Columns[i]+str(int(knight[1])+int(up)) +" or "+ Columns[i]+str(int(knight[1])+int(down)))
                        if((ColumnDestination+RowDestination).lower() == (Columns[i]+str(int(knight[1])+int(up))) or ((ColumnDestination+RowDestination).lower() == (Columns[i]+str(int(knight[1])+int(down))))):
                            move = knights[k] + (ColumnDestination+RowDestination).lower()
                            matchingknights[k] = (ColumnDestination+RowDestination).lower()
                            matchingcount = matchingcount + 1
                            
        if(matchingcount==2):
            print("two knights both able to make the same move --- will handle later")
        elif(matchingcount==1 ):
            print("one knight able to make the legal move -  easy")
            session_attr["whitePeices"]["knight"] = matchingknights
            return move 
        else:
            print("illegal move")
            return False
    def moveCreator(handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        Row = handler_input.request_envelope.request.intent.slots["Row"].value
        Column =handler_input.request_envelope.request.intent.slots["Column"].value
        PieceName = handler_input.request_envelope.request.intent.slots["PieceName"].value
        desination  =Column + Row
        StartingMove = session_attr["whitePeices"][PieceName]
        if(PieceName == "knight"):
            Move = ChessIntentHandler.knightHandler(Row,Column,session_attr)
            if(Move != False):
                Move = Move.lower()
                print(Move)
                ChessIntentHandler.MoveMaker(Move,session_attr,PieceName)
        if(PieceName == "pawn"):
            print("pawn")
        else:
            StartingMove = session_attr["whitePeices"][PieceName]
        return Move
    def test():
        print("test")
    def can_handle(self, handler_input):# this is taking the input from the user (chess move)
        return ask_utils.is_intent_name("MovePieceIntent")(handler_input)# checks if the input can be handled by this method
        # this returns a method call for handle if the input can be handled by this method
        
    def handle(self, handler_input):# this is the reponse from alexa -  will need to get move from chess api
        ChessIntentHandler.test()
        session_attr = handler_input.attributes_manager.session_attributes
        Row = handler_input.request_envelope.request.intent.slots["Row"].value
        Column =handler_input.request_envelope.request.intent.slots["Column"].value
        PieceName = handler_input.request_envelope.request.intent.slots["PieceName"].value
        move = ChessIntentHandler.moveCreator(handler_input)# this creates the move for UCI format
        speak_output = ChessIntentHandler.MoveMaker(move,session_attr,PieceName)
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ChessIntentHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()