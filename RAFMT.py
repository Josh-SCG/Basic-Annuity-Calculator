#for the gui
from tkinter import *

#for the fancy graph
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from math import floor, pow

# Assumption Variables
compound_interest_rate = 0.06
compound_period = 0 # must be calculated below
yearly_compound_period = 1 # Assumed at once a year (once a month will be 12 then)
interest_period = 1 # assuming added once a year
initial_fund_fees = 0.015 * 1.15 # Hollard's max fee * VAT
yearly_fund_fees = 0.01 * 1.15 # Hollard's max continual fee * VAT
yearly_inflation = 0.03 # Assumed based on previous years

#Main window and settings
root = Tk()
root.title("Retirement Annuity Tool")
root.configure(background="gray")
root.geometry("1320x660")
root.maxsize(1320,660)
root.minsize(1320,660)
root.option_add("*Font", "helvetica 13")

#Functions for tooltips and buttons
def on_button_hover(e):
    button = e.widget
    button["bg"] = "white"

def on_button_hover_leave(e):
    button = e.widget
    button["bg"] = "dark sea green"

def on_hover_age(e):
    tooltip_text.config(text = "  Your current age in years.     ")

def on_hover_retire_age(e):
    tooltip_text.config(text = "  The age you want to retire at (It is typically around 60-65).     ")

def on_hover_current_amount(e):
    tooltip_text.config(text = "  How much you currently have saved up for retirement and is the combined value of pots in the new system (in Rands).     ")

def on_hover_contribution(e):
    tooltip_text.config(text = "  How much you/your employer contribute towards retirement each month (in Rands).     ")

def on_hover_annual_draw(e):
    tooltip_text.config(text = "  How much you will draw from the fund in a year once retired.     ")

def on_hover_one_third(e):
    tooltip_text.config(text = "  When you retire, you're entitled to 1/3 of your fund. Will take it? If so, that is not included in the calculation.     ")

def hover_leave(e):
    tooltip_text.config(text = "   Hover over any input name to learn more about it.      ")

def assumptions_info():
    popup = Toplevel(root)
    popup.geometry("5600x200")
    popup.maxsize(560,250)
    popup.title("Assumptions")
    Label(popup, text="The calculations assume that:", wraplength = 560).pack()
    Label(popup, text="Compound Interest is calculated at 6 percent until retirement", wraplength = 560).pack()
    Label(popup, text="Compound interest is added once a year", wraplength = 560).pack()
    Label(popup, text="An inital fee on 1.5 percent is taken when the fund starts paying out", wraplength = 560).pack()
    Label(popup, text="A 1 percent fee is deducted yearly", wraplength = 560).pack()
    Label(popup, text="No funds were withdrawn until retierment age", wraplength = 560).pack()
    Label(popup, text="There is a constant 3 percent increase for inflation", wraplength = 560).pack()

#Functions for calculations#
def error_pop_up(error_text):
    popup = Toplevel(root)
    popup.geometry("400x100")
    popup.maxsize(400,100)
    popup.title("Input Error(s)")
    Label(popup, text=error_text, wraplength = 300).pack()

def big_boi_calc():
    #Variable set up
    age = age_entry.get()
    retire_age = retirement_age_entry.get()
    current_savings = current_amount_entry.get()
    monthly_contribution = monthy_contributions_entry.get()
    annual_draw_down = annual_draw_entry.get()
    draw_down_percent = draw_down_is_percent.get()
    one_third_check = one_third_check_var.get()

    #Input checks and Convert variable to approriate types
    try:
        age = int(age)
        retire_age = int(retire_age)
        current_savings = float(current_savings)
        monthly_contribution = float(monthly_contribution)
        annual_draw_down = float(annual_draw_down)
    except:
        error_pop_up("You have an error with your inputs. Please ensure there are no letters in the entry boxes and that each is filled in.")
        return
    
    if draw_down_percent and float(annual_draw_down) > 100.0:
        error_pop_up("Double check your input for the annuity amount and if you've checked the box for it being a percent.")
        return
    
    if draw_down_percent and (float(annual_draw_down) < 2.5 or float(annual_draw_down) > 17.5): # Seemingly industry standard amounts
        error_pop_up("The minimum withrawl amount p.a. is 2.5 percent with a max of 17.5 percent. Please check your drop down rate.")
        return

    if int(retire_age) - int(age) < 0:
        error_pop_up("Double check your ages input.")
        return
    

    #Un interst-ed basic contributions
    base_investment = current_savings + (monthly_contribution * 12 * (retire_age - age)) 

    # Adding interest based on assumed values
    compound_period = (retire_age - age) * yearly_compound_period
    total_at_retirement = base_investment * ((1+(compound_interest_rate/interest_period))) ** (interest_period * compound_period)

    # Check if taken 1/3 lump sum
    if one_third_check:
        total_at_retirement -= total_at_retirement/3

    # One last check
    if not draw_down_percent and (float(annual_draw_down) >= float(total_at_retirement)*0.175 or float(annual_draw_down) <= float(total_at_retirement)*0.025):
        error_pop_up("The minimum withrawl amount p.a. is 2.5 percent (which is R" + str(round(float(total_at_retirement)*0.025,2)) + ")  with a max of 17.5 percent (which is R" + str(round(float(total_at_retirement)*0.175,2)) + "). Please check your drop down rate.")
        return

    # Displaying montly payment
    monthly_income_display.configure(text = "R"+str(round(annual_draw_down/12, 2)))
    if draw_down_percent:
        new_annual = total_at_retirement * annual_draw_down/100
        annual_draw_down = new_annual
        monthly_income_display.configure(text = "R"+str(round(annual_draw_down/12, 2)))

    # Compiling data for graph
    x = [age] # Years
    y = [current_savings] # Amount in fund
    #Skipping first year as can be as little as a week to someones birthday 
    current_fund_total = current_savings
    calc_inflation = 1 
    for i in range(age+1, retire_age):
        x.append(i)
        calc_inflation = calc_inflation * yearly_inflation # assuming fixed inflation on both contributions(+) and total value (-)
        current_fund_total += (monthly_contribution * 12) * (1+calc_inflation) # basic contributions
        current_fund_total =  current_fund_total * ((1+(compound_interest_rate/interest_period))) ** (interest_period * yearly_compound_period) # add compound interest
        current_fund_total -= current_fund_total * calc_inflation
        y.append(current_fund_total)

    # Fund fees and possible lump sum
    last_known = y[-1]
    if one_third_check:
        x.append(x[-1]+1)
        last_known -= last_known/3
        last_known -= last_known * initial_fund_fees
        last_known =  last_known * ((1+(compound_interest_rate/interest_period))) ** (interest_period * yearly_compound_period) # add compound interest
        #calc_inflation = calc_inflation * yearly_inflation
        last_known -= last_known * yearly_inflation
        y.append(last_known)
    else: 
        x.append(x[-1]+1)
        last_known -= last_known * initial_fund_fees
        last_known =  last_known * ((1+(compound_interest_rate/interest_period))) ** (interest_period * yearly_compound_period) # add compound interest
        #calc_inflation = calc_inflation * yearly_inflation
        last_known -= last_known * yearly_inflation
        y.append(last_known)

    # Update Label
    total_at_retirement_display.configure(text = "R" + str(round(y[-1], 2)))

    # Calculate the drainage
    retirement_over_50 = FALSE
    while y[-1] > annual_draw_down:
        # If you get one hell of an annuity fund, it could just grow perpetually, this ensures it will either go till there's no longer a full year of funds
        # or your age will pass 100 (which seems like a fair point since life expectancy is around 85yrs in SA)
        if (x[-1]+1) > 100:
            retirement_over_50 = TRUE
            break
        
        x.append(x[-1]+1)
        last_known = y[-1]
        deductions = annual_draw_down + (last_known * yearly_fund_fees)
        last_known =  last_known * ((1+(compound_interest_rate/interest_period))) ** (interest_period * yearly_compound_period) # add compound interest
        #calc_inflation = calc_inflation * yearly_inflation
        last_known -= last_known * yearly_inflation
        y.append(last_known - deductions)

    if retirement_over_50:
        time_to_broke_display.configure(text = "50+ Years")
        fig.gca().set_xlim(age, 100)
    else:
        time_to_broke_display.configure(text = str(x[-1] - retire_age) + " Years")
    

    # Graph time
    fig.clear() # For multiple uses, don't want to draw on a old graph
    fig.add_subplot(111).plot(x,y) #subplot(111) is sorta the co-ords if you have multiple graphs on on figure 
    fig.gca().set_title("Annuity Funds over the Years")
    fig.gca().set_xlabel("Your Age (in years)")
    fig.gca().set_ylabel("Total Funds in Annuity (ZAR)")
    fig.gca().axes.yaxis.get_major_formatter().set_scientific(False) #Just fo R1000000 is not 1.0e-6
    canvas.draw() # Turtle


#Clearing input fields and return to blank slate
def clean_up():
    age_entry.delete(0, END)
    retirement_age_entry.delete(0, END)
    current_amount_entry.delete(0, END)
    monthy_contributions_entry.delete(0, END)
    annual_draw_entry.delete(0, END)
    total_at_retirement_display.configure(text = "R---")
    time_to_broke_display.configure(text = "---years")
    monthly_income_display.configure(text = "R---")
    #Need ti clear the figure and draw the blank
    fig.clear()
    canvas.draw()

#Section for user input
input_frame = Frame(root, width = 300, height = 540, bd=10, relief=RIDGE, background="light gray")
input_frame.grid(row = 0, column = 0, padx = 5, pady = 5)

# Follows as such for input fields:
# Creation
# Placement
# Add fancy hover functions (2 lines)
#
# Create enrty box
# Place box

age_label = Label(input_frame, text = "Age", background="light gray")
age_label.grid(row = 0, column = 0, padx = 5, pady = 10)
age_label.bind("<Enter>", on_hover_age)
age_label.bind("<Leave>", hover_leave)

age_entry = Entry(input_frame, bd=3)
age_entry.grid(row = 0, column = 1, padx = 5, pady = 10)


retirement_age_label = Label(input_frame, text = "Retirement Age", background="light gray")
retirement_age_label.grid(row = 1, column = 0, padx = 5, pady = 10)
retirement_age_label.bind("<Enter>", on_hover_retire_age)
retirement_age_label.bind("<Leave>", hover_leave)

retirement_age_entry = Entry(input_frame, bd=3)
retirement_age_entry.grid(row = 1, column = 1, padx = 5, pady = 10)


current_amount_label = Label(input_frame, text = "Current Retirement Savings", background="light gray")
current_amount_label.grid(row = 2, column = 0, padx = 5, pady = 10)
current_amount_label.bind("<Enter>", on_hover_current_amount)
current_amount_label.bind("<Leave>", hover_leave)

current_amount_entry = Entry(input_frame, bd=3)
current_amount_entry.grid(row = 2, column = 1, padx = 5, pady = 10)


monthy_contributions_label = Label(input_frame, text = "Monthy Contribution", background="light gray")
monthy_contributions_label.grid(row = 3, column = 0, padx = 5, pady = 10)
monthy_contributions_label.bind("<Enter>", on_hover_contribution)
monthy_contributions_label.bind("<Leave>", hover_leave)

monthy_contributions_entry = Entry(input_frame, bd=3)
monthy_contributions_entry.grid(row = 3, column = 1, padx = 5, pady = 10)


annual_draw_label = Label(input_frame, text = "Annual Draw Down", background="light gray")
annual_draw_label.grid(row = 4, column = 0, padx = 5, pady = 10)
annual_draw_label.bind("<Enter>", on_hover_annual_draw)
annual_draw_label.bind("<Leave>", hover_leave)

annual_draw_entry = Entry(input_frame, bd=3)
annual_draw_entry.grid(row = 4, column = 1, padx = 5, pady = 10)


draw_down_is_percent = BooleanVar()
annual_draw_percent_label = Label(input_frame, text = "Is the annual draw down in percent?", background="light gray")
annual_draw_percent_label.grid(row = 5, column = 0, padx = 5, pady = 10)
annual_draw_percent_label.bind("<Enter>", on_hover_annual_draw)
annual_draw_percent_label.bind("<Leave>", hover_leave)

annual_draw_percent_check_button = Checkbutton(input_frame, text = "Check if 'Yes'", variable = draw_down_is_percent, background="light gray")
annual_draw_percent_check_button.grid(row = 5, column = 1, padx = 5, pady = 10)


one_third_check_var = BooleanVar()
one_third_label = Label(input_frame, text = "Will you withraw the 1/3 at retirement?", background="light gray")
one_third_label.grid(row = 6, column = 0, padx = 5, pady = 10)
one_third_label.bind("<Enter>", on_hover_one_third)
one_third_label.bind("<Leave>", hover_leave)

one_third_check_button = Checkbutton(input_frame, text = "Check if 'Yes'", variable = one_third_check_var, background="light gray")
one_third_check_button.grid(row = 6, column = 1, padx = 5, pady = 10)

submit_button = Button(input_frame, text = "Submit", bg = "dark sea green", command = big_boi_calc)
submit_button.grid(row = 7,column = 0, padx = 5, pady = 10)
submit_button.bind("<Enter>", on_button_hover)
submit_button.bind("<Leave>", on_button_hover_leave)

clear_button = Button(input_frame, text = "Clear", bg = "dark sea green", command = clean_up)
clear_button.grid(row = 7,column = 1, padx = 5, pady = 10)
clear_button.bind("<Enter>", on_button_hover)
clear_button.bind("<Leave>", on_button_hover_leave)


#Section to display total amounts and other info
total_section = Frame(root, width = 300, height = 60, bd=10, relief=RIDGE, background="light gray")
total_section.grid(row = 1, column = 0, padx = 5, pady = 5)

total_at_retirement_label = Label(total_section, text = "Total Savings at Retirement", background="light gray")
total_at_retirement_label.grid(row = 0, column = 0, padx = 5, pady = 10)

total_at_retirement_display = Label(total_section, text = "R---", background="light gray")
total_at_retirement_display.grid(row = 0, column = 1, padx = 5, pady = 10)


monthly_income_label = Label(total_section, text = "Monthly income for retirement", background="light gray")
monthly_income_label.grid(row = 1, column = 0, padx = 5, pady = 10)

monthly_income_display = Label(total_section, text = "R---", background="light gray")
monthly_income_display.grid(row = 1, column = 1, padx = 5, pady = 10)


time_to_broke_label = Label(total_section, text = "Annuity would last", background="light gray")
time_to_broke_label.grid(row = 2, column = 0, padx = 5, pady = 10)

time_to_broke_display = Label(total_section, text = "---years", background="light gray")
time_to_broke_display.grid(row = 2, column = 1, padx = 5, pady = 10)

#Data visualisation section
data_visual_section = Frame(root, width = 800, height = 610, background="light gray")
data_visual_section.grid(row = 0, rowspan = 2, column = 1, padx = 10, pady = 5)

# Instace area for graph
fig = Figure(figsize=(8,6), dpi =100)
canvas = FigureCanvasTkAgg(fig, master=data_visual_section)  # A Tkinter DrawingArea
canvas.draw()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

#Tooltip section
tooltip_section = Frame(root, width = 1040, height = 30, background="light gray")
tooltip_section.grid(row = 2, columnspan = 2, column = 0, padx = 5, pady = 5, sticky = 'W')
tooltip_text = Label(tooltip_section, text="   Hover over any input name to learn more about it.      ", bd=1, relief=SUNKEN, anchor=E, background="light gray")
tooltip_text.grid(row = 0, column = 1)

assumptions_button = Button(tooltip_section, text = "Assumptions", bg = "dark sea green", command = assumptions_info)
assumptions_button.grid(row = 0, column =0, padx = 5)
assumptions_button.bind("<Enter>", on_button_hover)
assumptions_button.bind("<Leave>", on_button_hover_leave)


#######
# Run #
#######
root.mainloop()