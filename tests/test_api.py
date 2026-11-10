
from unittest.mock import patch
from chatbot.app import start_chatbot


def test_chatbot_displays_welcome_message():

    with patch("builtins.input", side_effect=["exit"]):
        with patch("builtins.print") as mock_print:

            start_chatbot()

            mock_print.assert_any_call(
                "Welcome to CustomerCare AI!"
            )


def test_chatbot_exits_when_user_types_exit():

    with patch("builtins.input", side_effect=["exit"]):
        with patch("builtins.print") as mock_print:

            start_chatbot()

            mock_print.assert_any_call(
                "CustomerCare AI: Thank you for contacting us. Goodbye!"
            )


def test_chatbot_displays_ai_response():

    with patch("builtins.input", side_effect=["Where is my order?", "exit"]):
        with patch("chatbot.app.generate_response", return_value="Your order is on its way."):

            with patch("builtins.print") as mock_print:

                start_chatbot()

                mock_print.assert_any_call(
                    "\nCustomerCare AI:", "Your order is on its way."
                )


def test_chatbot_handles_api_error():

    with patch("builtins.input", side_effect=["Hello", "exit"]):
        with patch(
            "chatbot.app.generate_response",
            side_effect=Exception("API connection failed")
        ):
            with patch("builtins.print") as mock_print:

                start_chatbot()

                mock_print.assert_any_call(
                    "\nCustomerCare AI: Sorry, something went wrong."
                )
def test_app_entry_point():

    import runpy

    with patch("builtins.input", side_effect=["exit"]):
        with patch("builtins.print") as mock_print:

            runpy.run_module(
                "chatbot.app",
                run_name="__main__"
            )

            mock_print.assert_any_call(
                "Welcome to CustomerCare AI!"
            )