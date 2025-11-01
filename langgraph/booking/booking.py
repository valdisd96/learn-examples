import os
import getpass
import uuid
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage

# Define LLM Model
def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("ANTHROPIC_API_KEY")

llm = ChatAnthropic(model="claude-3-haiku-20240307")

# Booking details (Added room numbers)
bookings = {
    "123": {"status": "confirmed", "name": "Alice Johnson", "guests": 2, "room": "101"},
    "456": {"status": "pending", "name": "Bob Smith", "guests": 3, "room": "TBD"},
    "789": {"status": "not_found"},
}

@tool
def greet_user(username: str) -> str:
    """Greets the user with a welcome message."""
    return f"Hello {username}, Welcome to Hotel ABC. How can I help you?"

@tool
def check_booking(guest_id: str) -> str:
    """Check bookings for a given booking ID."""
    booking = bookings.get(guest_id, {"status": "not_found"})
    
    if booking["status"] == "confirmed":
        return f"Booking confirmed for {booking['name']} with {booking['guests']} guests. Your assigned room is {booking['room']}."
    elif booking["status"] == "pending":
        return f"Booking pending for {booking['name']} with {booking['guests']} guests. Your room number is yet to be assigned. Please visit the reception."
    else:
        return "No booking found. Would you like to make a reservation?"

@tool
def confirmed_check_in(guest_id: str) -> str:
    """Confirm check-in for a given booking ID."""
    booking = bookings.get(guest_id, {"status": "not_found"})
    
    if booking["status"] == "confirmed":
        return f"Hello {booking['name']}, Welcome! Your room {booking['room']} is ready for {booking['guests']} guests."
    else:
        return "Your booking is either pending or not found. Please visit the reception."

@tool
def pending_check_in(guest_id: str) -> str:
    """Handle pending check-in cases."""
    booking = bookings.get(guest_id, {"status": "not_found"})
    
    if booking["status"] == "pending":
        return f"Hello {booking['name']}, your booking for {booking['guests']} guests is pending. Your room assignment is not yet available. Please visit the reception to complete the process."
    else:
        return "No pending booking found."

@tool
def no_booking(input: str = "") -> str:
    """Handle cases where no booking is found."""
    return "No booking found. Would you like to make a reservation?"

@tool
def provide_hotel_info(input: str) -> str:
    """Provides information about the hotel."""
    return (
        "Hotel ABC offers luxury suites, fine dining, and spa services. "
        "Our rooms are equipped with premium amenities. Our address is 5432, Test street, CA, 19893. "
        "We have additional parking at ...."
        " Let us know if you need assistance."
    )

@tool
def request_room_service(guest_id: str) -> str:
    """Requests room service for a given booking ID."""
    booking = bookings.get(guest_id, {"status": "not_found"})
    
    if booking["status"] == "confirmed":
        return f"Room service has been requested for room {booking['room']}. Our staff will be with you shortly."
    else:
        return "Room service is only available for confirmed bookings. Please check with the reception."

@tool
def report_issue(guest_id: str) -> str:
    """Allows guests to report any issues."""
    booking = bookings.get(guest_id, {"status": "not_found"})
    
    if booking["status"] == "confirmed":
        return f"Thank you, Mr./Ms. {booking['name']}. Your issue has been received. We apologize for the inconvenience, and our team will fix it soon."
    else:
        return "No booking found."

# Routing Function
def route_request(state):
    user_input = state["messages"][-1].content.strip().lower()
    if "greet" in user_input:
        return {"next_node": "process_greet"}
    elif "check booking" in user_input:
        return {"next_node": "process_check_bookings"}
    elif "confirmed check-in" in user_input or "confirm booking" in user_input:
        return {"next_node": "process_confirmed_check_in"}
    elif "pending check-in" in user_input:
        return {"next_node": "process_pending_check_in"}
    elif "no booking" in user_input:
        return {"next_node": "process_no_booking"}
    elif "hotel info" in user_input:
        return {"next_node": "process_hotel_info"}
    elif "room service" in user_input:
        return {"next_node": "process_room_service"}
    elif "report issue" in user_input:
        return {"next_node": "process_report_issue"}
    else:
        return {"next_node": END}

# Processing Functions
def process_greet(state):
    username = state["messages"][-1].content.strip().replace("greet", "").strip()
    response = greet_user.invoke(username)
    return {"messages": [AIMessage(content=response)]}

def process_check_bookings(state):
    guest_id = state["messages"][-1].content.strip().replace("check booking", "").strip()
    response = check_booking.invoke(guest_id)
    return {"messages": [AIMessage(content=response)]}

def process_confirmed_check_in(state):
    content = state["messages"][-1].content.strip()
    guest_id = content.replace("confirm booking", "").replace("confirmed check-in", "").strip()
    response = confirmed_check_in.invoke(guest_id)
    return {"messages": [AIMessage(content=response)]}

def process_pending_check_in(state):
    guest_id = state["messages"][-1].content.strip().replace("pending check-in", "").strip()
    response = pending_check_in.invoke(guest_id)
    return {"messages": [AIMessage(content=response)]}

def process_no_booking(state):
    response = no_booking.invoke("")
    return {"messages": [AIMessage(content=response)]}

def process_hotel_info(state):
    input_text = state["messages"][-1].content.strip().replace("hotel info", "").strip()
    response = provide_hotel_info.invoke(input_text)
    return {"messages": [AIMessage(content=response)]}

def process_room_service(state):
    guest_id = state["messages"][-1].content.strip().replace("room service", "").strip()
    response = request_room_service.invoke(guest_id)
    return {"messages": [AIMessage(content=response)]}

def process_report_issue(state):
    guest_id = state["messages"][-1].content.strip().replace("report issue", "").strip()
    response = report_issue.invoke(guest_id)
    return {"messages": [AIMessage(content=response)]}

# Define Workflow Class
class State(TypedDict):
    messages: Annotated[list, add_messages]
    next_node: str

# Setup Workflow
memory = MemorySaver()
workflow = StateGraph(State)
workflow.add_node("route_request", route_request)
workflow.add_node("process_greet", process_greet)
workflow.add_node("process_check_bookings", process_check_bookings)
workflow.add_node("process_confirmed_check_in", process_confirmed_check_in)
workflow.add_node("process_pending_check_in", process_pending_check_in)
workflow.add_node("process_no_booking", process_no_booking)
workflow.add_node("process_hotel_info", process_hotel_info)
workflow.add_node("process_room_service", process_room_service)
workflow.add_node("process_report_issue", process_report_issue)

# Define Transitions
workflow.add_edge(START, "route_request")
workflow.add_conditional_edges(
    "route_request", 
    lambda state: state["next_node"],
    {
        "process_greet": "process_greet",
        "process_check_bookings": "process_check_bookings",
        "process_confirmed_check_in": "process_confirmed_check_in",
        "process_pending_check_in": "process_pending_check_in",
        "process_no_booking": "process_no_booking",
        "process_hotel_info": "process_hotel_info",
        "process_room_service": "process_room_service",
        "process_report_issue": "process_report_issue",
        END: END
    }
)

# Add edges from processing nodes to END
workflow.add_edge("process_greet", END)
workflow.add_edge("process_check_bookings", END)
workflow.add_edge("process_confirmed_check_in", END)
workflow.add_edge("process_pending_check_in", END)
workflow.add_edge("process_no_booking", END)
workflow.add_edge("process_hotel_info", END)
workflow.add_edge("process_room_service", END)
workflow.add_edge("process_report_issue", END)

# Compile the Workflow
graph = workflow.compile(checkpointer=memory)

with open("booking.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())
print("Workflow diagram saved to booking.png")

print("\nSystem Ready! Type 'q' to quit.")
print("Welcome! You can:")
print("--> Greet users (e.g., 'greet John')")
print("--> Check bookings (e.g., 'check booking 123')")
print("--> Confirm bookings (e.g., 'confirm booking 123')")
print("--> Get hotel info (e.g., 'hotel info')")
print("--> Request room service (e.g., 'room service 123')")
print("--> Report an issue (e.g., 'report issue 123')")
print("Type 'q' to quit.\n")

config = {"configurable": {"thread_id": str(uuid.uuid4())}}

while True:
    user = input("User: ")
    if user.lower() in {"q", "quit"}:
        print("Goodbye!")
        break
    output = graph.invoke({"messages": [HumanMessage(content=user)]}, config=config)
    print("AI:", output["messages"][-1].content)