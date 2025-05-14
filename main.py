import os
from user_information import UserInformation
from personal_record import PersonalRecord
from goals import Goals
from diet_plan import generate_and_display_meal_plan
import re

if not os.path.exists("database"):
    os.makedirs("database")

def main():
    print("Welcome to Health Tracker.")

    ui = UserInformation()
    record = PersonalRecord()
    g = Goals()

    while True:
        print("\nHome:")
        print("\n1. Sign up")
        print("\n2. Log in")
        print("\n3. Exit")
        choice = input("\nPlease choose an option (1, 2, or 3): ").strip()

        if choice == "1":
            print("\nPlease enter your information")
            #Validate username and display error message
            while True: 
                username = input("Username (3-8 characters): ").strip()
                if 3 <= len(username) <= 8:
                    break
                print("Your username must be between 3 and 8 characters.")

            #Validate email and display error message
            email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
            while True:
                email = input("Email: ").strip()
                if re.match(email_regex, email):
                    break
                print("Invalid email address.")
            
            #Validate password and display error message
            while True:
                password = input("Password: ").strip()
                if len(password) >= 8:
                    break
                print("Your password must be at least 8 characters long.")

            #Validate first name
            while True:
                first_name = input("First Name: ").strip()
                if first_name:
                    break
                print("First name cannot be empty.")
            
            #Validate last name
            while True:
                last_name = input("Last Name: ").strip()
                if last_name:
                    break
                print("Last name cannot be empty.")

            #Validate year of birth. User should be at least 13 years
            while True:
                try:
                    year_of_birth = int(input("Year of Birth: "))
                    if 1945 <= year_of_birth <= 2012:
                        break
                    else:
                        print("Please enter a valid year of birth. User must be at least 13 year old.")
                except ValueError:
                    print("Invalid year. Please input 4-digits year.")

            while True:
                gender = input("Gender (male or female): ").strip().lower()
                if gender in ['male', 'female']:
                    break
                else:
                    print("Invalid input.")

            success, message = ui.user_account(username, email, password, first_name, last_name, year_of_birth, gender)
            print(message)

        elif choice == "2":
            print("\nLog in: ")
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            success, message = ui.login(username, password)
            print(message) 

            if success:
                while True:
                    print(f"\nHi {username}")
                    print("\n1. View Your User Account")
                    print("\n2. View Your Health Record")
                    print("\n3. View Your Workout Status")
                    print("\n4. Set Up Personal Goals")
                    print("\n5. View Your Diet Plan")
                    print("\n6. Logout")

                    option = input("\nPlease choose your options (1, 2, 3, 4, 5, or 6): ").strip()

                    if option == "1":
                        profile = ui.get_user_profile(username)
                        if profile:
                            print("\nYour profile: ")
                            for key, value in profile.items():
                                print(f"{key.capitalize()}: {value}")
                        else:
                            print("Your profile not found")

                    elif option == "2":
                        print("\nYour Health Record:")

                        data = record.get_health_data(username)
                        if data:
                            for key, value in data.items():
                                print(f"{key.replace('_', ' ').capitalize()}: {value}")

                            while True:
                                update_health = input("\nDo you want to update your health record? (y/n): ").strip().lower()
                                if update_health == "y":
                                    try:
                                        weight = float(input("Enter your weight in kg: ").strip())
                                        height_cm = float(input("Enter your height in cm: ").strip())
                                        height = height_cm / 100
                                        success, message = record.add_or_update_measurements(username, weight, height)
                                        print(message)
                                    except ValueError:
                                        print("Please enter numeric values for weight and height.")
                                    break
                                elif update_health == "n":
                                    break
                                else:
                                    print("Invalid input. Please enter 'y' for yes or 'n' for no.")

                        else:
                            print("No health record found.")
                            try:
                                weight = float(input("Enter your weight in kg: ").strip())
                                height_cm = float(input("Enter your height in cm: ").strip())
                                height = height_cm / 100

                                success, message = record.add_or_update_measurements(username, weight, height)
                                print(message)

                            except ValueError:
                                print("Please enter valid numeric values.")

                    elif option == "3":
                        print("\nYour Workout Status:")

                        workout_data = ui.get_workout_status(username)
                        if workout_data:
                            for key, value in workout_data.items():
                                print(f"{key}: {value}")
                            while True:
                                update_workout = input("Do you want to update your workout status? (y/n): ").strip().lower()
                                if update_workout == "y":
                                    try:
                                        workout_days = int(input("How many days do you work out per week (0-7 days)? "))
                                        duration = float(input("How many hours per day do you workout? "))
                                        success, message = ui.update_workout_status(username, workout_days, duration)
                                        print(message)

                                    except ValueError:
                                        print("Invalid input. Please enter numeric values. ")
                                    break
                                elif update_workout == "n":
                                    break
                                else:
                                    print("Invalid input. Please enter 'y' for yes or 'n' for no.")

                        else:
                            print("You have not input your workout status yet.")
                            try:
                                workout_days = int(input("Enter workout days per week (0–7): ").strip())
                                duration = float(input("Enter average duration per day (in hours): ").strip())
                                success, message = ui.update_workout_status(username, workout_days, duration)
                                print(message)

                            except ValueError:
                                print("Please enter valid numeric values.")

                    elif option == "4":
                        print("\nCurrent Personal Goals:")

                        personal_goals = g.get_goals(username)
                        if personal_goals:
                            for key, value in personal_goals.items():
                                print(f"{key}: {value}")
                            while True:
                                update_goals = input("Do you want to update your personal goals? (y/n): ").strip().lower()
                                if update_goals == "y":
                                    try:
                                        goal = input("How do you want to manage your weight? (maintain, lose, or gain)? ").strip().lower()
                                        success, message = g.set_calorie_goal(username, goal)
                                        print(message)

                                    except ValueError:
                                        print("Invalid input.")
                                    break
                                elif update_goals == "n":
                                    break
                                else: 
                                    print("Invalid input. Please enter 'y' for yes and 'n' for no.")
                            
                        else:
                            print("You have not input your personal goals yet.")
                            try:
                                goal = input("How do you want to manage your weight? (maintain, lose, or gain)? ").strip().lower()
                                success, message = g.set_calorie_goal(username, goal)
                                print(message)
                            except ValueError:
                                print("Invalid input.")

                    elif option == "5":
                        print("\nGenerating your 7-day meal plan:")
                        try:
                            generate_and_display_meal_plan(username)
                        except Exception as e:
                            print(f"Failed to generate meal plan: {e}")

                    elif option == "6":
                        print("Logging out ...")
                        break

                    else:
                        print("Invalid choice. Please try again: ")

        elif choice == "3":
            print("Thank you!")
            break

        else:
            print("Invalid choice. Please try again: ")

    ui.close()
    record.close()

if __name__ == "__main__":
    main()           
