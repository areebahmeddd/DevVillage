from auth_routes import session_remove_if_not_verified
from flask import Blueprint, render_template


dashboard_blueprint = Blueprint(
    "dashboard", __name__, static_folder="static", template_folder="templates"
)

# DISCOVER
@dashboard_blueprint.route('/dashboard')
def discover():
    session_remove_if_not_verified()

    return render_template("dashboard.html")