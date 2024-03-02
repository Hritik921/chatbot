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
import requests 
import pandas as pd
from ask_sdk_model import Response
import io
import calendar
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome, you can say Hello or Help. Which would you like to try? Movie Recommender Or Zodiac Sign"
        repromt='try , get zodiac sign or suggest a movie'

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(repromt)
                .response
        )


class CaptureZodiacSignIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CaptureZodiacSignIntent")(handler_input)

    def filter(self, X):

        date = X.split()

        month = date[0]

        month_as_index = list(calendar.month_abbr).index(month[:3].title())

        day = int(date[1])

        return (month_as_index,day)

    def handle(self, handler_input):

        slots = handler_input.request_envelope.request.intent.slots

        year=slots["year"].value

        month = slots["month"].value

        day=slots["day"].value

        #ENTER YOUR URL HERE

        url ="https://docs.google.com/spreadsheets/d/e/2PACX-1vT-3jmBNLGTsHMvzNwFv18MTtWvTabtyjO7n9nxyAEG3-hho_jiJ7T_dQSQhtspMg/pub?output=csv"

        csv_content = requests.get(url).content

        df= pd.read_csv(io.StringIO(csv_content.decode('utf-8')))

        zodiac = ''

        month_as_index = list(calendar.month_abbr).index(month[:3].title())

        usr_dob = (month_as_index, int(day))

        for index, row in df.iterrows():
            if self.filter(row['Start']) <= usr_dob <= self.filter(row['End']): 
                zodiac=row['Zodiac'] 

        speak_output = 'I see you were born on the {day} of {month} {year}, which means that your zodiac sign will be {zodiac}.'.format(month= month, day= day, year=year, zodiac =zodiac)

        return (handler_input.response_builder.speak(speak_output).response)



class SuggestMovieIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("SuggestMovieIntent")(handler_input)

    def get_movies(self, language, genre, actor):
        url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRqvTIXuxKcr3PhReaWWMEReBxMj-xBIgqcnljKT8sA4Fi4YevKea5dhzjVk_sHsDrak6E2y1dJI-FZ/pub?output=csv'
        response = requests.get(url).content
        
        # Use pandas to read CSV data into a DataFrame
        df= pd.read_csv(io.StringIO(response.decode('utf-8')))
        
        # Filter DataFrame based on user preferences
        if language:
            df = df[df['Language'].str.lower() == language.lower()]
        if genre:
            df = df[df['Genre'].str.lower() == genre.lower()]
        if actor:
            df = df[df['Actor'].str.lower() == actor.lower()]
        
        # Get titles of matching movies
        movies = df['Movie'].tolist()
        
        return movies


    def handle(self, handler_input):
        language = ask_utils.get_slot_value(handler_input=handler_input, slot_name="language")
        genre = ask_utils.get_slot_value(handler_input=handler_input, slot_name="genre")
        actor = ask_utils.get_slot_value(handler_input=handler_input, slot_name="actor")
        
        movies = self.get_movies(language, genre, actor)
        
        speak_output = "Based on your preferences, I suggest the following movies: " if movies else "Sorry, I couldn't find any movies matching your criteria."
        speak_output += ", ".join(movies) if movies else ""
        print(movies)
        print(speak_output)
        return (
            handler_input.response_builder
            .speak(speak_output)
            .response
        )
        
    """   movies = self.get_movies(language, genre, actor)
        print(movies)
        speak_output1=''
        if not movies:
            speak_output = "Sorry, I couldn't find any movies matching your criteria."
            return (handler_input.response_builder.speak(speak_output).response)
        else:
            speak_output1 = "Based on your preferences, I suggest the following movies: "
            for movie in movies:
                speak_output1 += f"{movie}, "
            speak_output1 = speak_output1[:-2] 
        print(speak_output1)
        
        movie_output=speak_output1
        return (handler_input.response_builder.speak(movie_output).response)"""




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

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

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
sb.add_request_handler(CaptureZodiacSignIntentHandler())
sb.add_request_handler(SuggestMovieIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()