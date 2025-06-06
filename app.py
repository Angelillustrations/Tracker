import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import json
import os
import calendar

# Set page config
st.set_page_config(
    page_title="Daily Lifestyle Tracker",
    page_icon="📊",
    layout="wide"
)

# Function to save data to local JSON file
def save_data():
    try:
        # Convert date objects to strings for JSON serialization
        data_to_save = {}
        for date_str, data in st.session_state.tracker_data.items():
            data_to_save[date_str] = data.copy()
            
        with open('lifestyle_tracker_data.json', 'w') as f:
            json.dump(data_to_save, f, indent=2, default=str)
    except Exception as e:
        st.error(f"Error saving data: {e}")

# Function to load data from local JSON file
def load_data():
    try:
        if os.path.exists('lifestyle_tracker_data.json'):
            with open('lifestyle_tracker_data.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return {}

# Initialize session state for data storage
if 'tracker_data' not in st.session_state:
    st.session_state.tracker_data = load_data()

# Function to get program dates
def get_program_info():
    start_date = date(2025, 6, 2)  # June 2, 2025
    end_date = start_date + timedelta(weeks=30)
    return start_date, end_date

# Function to get week number from date
def get_week_number(target_date):
    start_date, _ = get_program_info()
    if isinstance(target_date, str):
        target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    
    days_diff = (target_date - start_date).days
    week_num = (days_diff // 7) + 1
    return max(1, min(30, week_num))

# Function to check if strength training is available
def is_strength_available(target_date):
    week_num = get_week_number(target_date)
    return week_num >= 3

# Function to get summary stats
def get_summary_stats(data_dict):
    if not data_dict:
        return {}
    
    total_days = len(data_dict)
    total_treadmill = sum(data.get('treadmill_time', 0) or 0 for data in data_dict.values())
    total_steps = sum(data.get('steps', 0) or 0 for data in data_dict.values()) # Changed 'additional_walk' to 'steps'
    total_lunch_walks = sum(data.get('lunch_walk_time', 0) or 0 for data in data_dict.values())
    strength_sessions = sum(1 for data in data_dict.values() if data.get('strength_training', False))
    
    # Calculate total exercise time including lunch walks
    total_exercise_time = total_treadmill + (total_steps / 100) + total_lunch_walks # Assuming 100 steps roughly equals 1 minute for cumulative calculation, adjust as needed
    
    # Handle None values properly for weights and blood sugar
    weights = []
    blood_sugars = []
    
    for data in data_dict.values():
        weight = data.get('weight')
        if weight is not None and weight > 0:
            weights.append(weight)
        
        blood_sugar = data.get('blood_sugar')
        if blood_sugar is not None and blood_sugar > 0:
            blood_sugars.append(blood_sugar)
    
    return {
        'total_days': total_days,
        'total_treadmill': total_treadmill,
        'avg_treadmill': total_treadmill / total_days if total_days > 0 else 0,
        'total_steps': total_steps, # Changed 'total_walks' to 'total_steps'
        'avg_steps': total_steps / total_days if total_days > 0 else 0, # Changed 'avg_walks' to 'avg_steps'
        'total_lunch_walks': total_lunch_walks,
        'avg_lunch_walks': total_lunch_walks / total_days if total_days > 0 else 0,
        'total_exercise_time': total_exercise_time,
        'avg_exercise_time': total_exercise_time / total_days if total_days > 0 else 0,
        'strength_sessions': strength_sessions,
        'avg_weight': sum(weights) / len(weights) if weights else 0,
        'latest_weight': weights[-1] if weights else 0,
        'avg_blood_sugar': sum(blood_sugars) / len(blood_sugars) if blood_sugars else 0,
        'weight_change': weights[-1] - weights[0] if len(weights) > 1 else 0
    }

def main():
    st.title("🏃‍♂️ Daily Lifestyle Tracker")
    st.markdown("Track your daily journey to better health and wellness!")
    
    start_date, end_date = get_program_info()
    
    # Sidebar for navigation
    st.sidebar.title("📅 Navigation")
    
    # View selection
    view_mode = st.sidebar.selectbox(
        "Select View:",
        ["Daily Entry", "Weekly Summary", "Monthly Summary", "All-Time Summary"]
    )
    
    if view_mode == "Daily Entry":
        show_daily_entry()
    elif view_mode == "Weekly Summary":
        show_weekly_summary()
    elif view_mode == "Monthly Summary":
        show_monthly_summary()
    else:
        show_alltime_summary()

def show_daily_entry():
    st.header("📝 Daily Entry")
    
    # Date selection
    start_date, end_date = get_program_info()
    selected_date = st.date_input(
        "Select Date:",
        value=date.today() if start_date <= date.today() <= end_date else start_date,
        min_value=start_date,
        max_value=end_date
    )
    
    date_str = selected_date.strftime("%Y-%m-%d")
    week_num = get_week_number(selected_date)
    
    st.info(f"📅 {selected_date.strftime('%A, %B %d, %Y')} - Week {week_num} of 30")
    
    # Form for daily entry
    with st.form(f"daily_entry_{date_str}"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏃‍♂️ Exercise")
            
            treadmill_time = st.number_input(
                "Treadmill Time (minutes)",
                min_value=0,
                max_value=300,
                value=st.session_state.tracker_data.get(date_str, {}).get('treadmill_time', 0),
                help="Enter treadmill time for today"
            )
            
            steps = st.number_input( # Changed 'additional_walk' to 'steps'
                "Steps (count)", # Changed label
                min_value=0,
                max_value=50000, # Increased max value for steps
                value=st.session_state.tracker_data.get(date_str, {}).get('steps', 0), # Changed variable name
                step=100, # Added step for steps
                help="Enter total steps for the day" # Changed help text
            )
            
            lunch_walk_time = st.number_input(
                "Lunch Walk Time (minutes)",
                min_value=0,
                max_value=120,
                value=st.session_state.tracker_data.get(date_str, {}).get('lunch_walk_time', 0),
                help="Enter lunch walk time"
            )
            
            # Strength training availability
            if is_strength_available(selected_date):
                strength_training = st.checkbox(
                    "Strength Training Completed",
                    value=st.session_state.tracker_data.get(date_str, {}).get('strength_training', False),
                    help="Check if you completed strength training today"
                )
            else:
                strength_training = False
                st.info("💪 Strength training starts from Week 3")
        
        with col2:
            st.subheader("📊 Health Metrics")
            
            weight = st.number_input(
                "Weight (kg)",
                min_value=0.0,
                max_value=300.0,
                value=st.session_state.tracker_data.get(date_str, {}).get('weight', 0.0),
                step=0.1,
                help="Enter your weight for today"
            )
            
            blood_sugar = st.number_input(
                "Blood Sugar Reading (optional)",
                min_value=0.0,
                max_value=500.0,
                value=st.session_state.tracker_data.get(date_str, {}).get('blood_sugar', 0.0),
                step=0.1,
                help="Enter blood sugar reading if available"
            )
            
            st.subheader("😊 Mood & Energy")
            mood_energy = st.text_area(
                "How did you feel today?",
                value=st.session_state.tracker_data.get(date_str, {}).get('mood_energy', ''),
                max_chars=256,
                help="Describe your mood and energy levels (max 256 characters)",
                height=100
            )
        
        submitted = st.form_submit_button("💾 Save Today's Data", use_container_width=True)
        
        if submitted:
            # Store data
            st.session_state.tracker_data[date_str] = {
                'date': date_str,
                'week': week_num,
                'treadmill_time': treadmill_time,
                'steps': steps, # Changed 'additional_walk' to 'steps'
                'lunch_walk_time': lunch_walk_time,
                'strength_training': strength_training,
                'weight': weight if weight and weight > 0 else None,
                'blood_sugar': blood_sugar if blood_sugar and blood_sugar > 0 else None,
                'mood_energy': mood_energy
            }
            
            st.success(f"✅ Data saved for {selected_date.strftime('%B %d, %Y')}!")
            save_data()
    
    # Show recent entries
    if st.session_state.tracker_data:
        st.subheader("📋 Recent Entries")
        recent_data = dict(sorted(st.session_state.tracker_data.items(), reverse=True)[:7])
        
        for date_str, data in recent_data.items():
            with st.expander(f"{date_str} - Week {data.get('week', 'N/A')}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"🏃‍♂️ Treadmill: {data.get('treadmill_time', 0)} min")
                    st.write(f"🚶‍♂️ Steps: {data.get('steps', 0)}") # Changed label and variable
                with col2:
                    st.write(f"🍽️ Lunch Walk: {data.get('lunch_walk_time', 0)} min")
                    st.write(f"💪 Strength: {'✅' if data.get('strength_training') else '❌'}")
                with col3:
                    if data.get('weight'):
                        st.write(f"⚖️ Weight: {data.get('weight')} kg")
                    if data.get('blood_sugar'):
                        st.write(f"🩸 Blood Sugar: {data.get('blood_sugar')}")
                
                if data.get('mood_energy'):
                    st.write(f"😊 Mood: {data.get('mood_energy')}")

def show_weekly_summary():
    st.header("📊 Weekly Summary")
    
    # Week selection
    selected_week = st.selectbox(
        "Select Week:",
        range(1, 31),
        format_func=lambda x: f"Week {x}"
    )
    
    # Calculate week date range
    start_date, _ = get_program_info()
    week_start = start_date + timedelta(weeks=selected_week-1)
    week_end = week_start + timedelta(days=6)
    
    st.info(f"📅 Week {selected_week}: {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")
    
    # Get week data
    week_data = {}
    for i in range(7):
        day_date = week_start + timedelta(days=i)
        date_str = day_date.strftime("%Y-%m-%d")
        if date_str in st.session_state.tracker_data:
            week_data[date_str] = st.session_state.tracker_data[date_str]
    
    if week_data:
        # Weekly stats
        stats = get_summary_stats(week_data)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Days Logged", stats['total_days'])
            st.metric("Total Treadmill", f"{stats['total_treadmill']} min")
        with col2:
            st.metric("Total Steps", f"{stats['total_steps']}") # Changed label
            st.metric("Total Lunch Walks", f"{stats['total_lunch_walks']} min")
        with col3:
            st.metric("Total Exercise Time", f"{stats['total_exercise_time']} min")
            st.metric("Avg Exercise/Day", f"{stats['avg_exercise_time']:.1f} min")
        with col4:
            st.metric("Strength Sessions", stats['strength_sessions'])
            if stats['avg_weight'] > 0:
                st.metric("Avg Weight", f"{stats['avg_weight']:.1f} kg")
        
        # Daily breakdown
        st.subheader("📅 Daily Breakdown")
        daily_df = []
        for i in range(7):
            day_date = week_start + timedelta(days=i)
            date_str = day_date.strftime("%Y-%m-%d")
            day_name = day_date.strftime("%A")
            
            if date_str in week_data:
                data = week_data[date_str]
                total_day_exercise = (data.get('treadmill_time', 0) + 
                                      (data.get('steps', 0) / 100) + # Using steps in total exercise calculation
                                      data.get('lunch_walk_time', 0))
                daily_df.append({
                    'Day': day_name,
                    'Date': day_date.strftime("%m/%d"),
                    'Treadmill': data.get('treadmill_time', 0),
                    'Steps': data.get('steps', 0), # Changed label
                    'Lunch Walk': data.get('lunch_walk_time', 0),
                    'Total Exercise': total_day_exercise,
                    'Strength': '✅' if data.get('strength_training') else '❌',
                    'Weight': f"{data.get('weight', 0):.1f}" if data.get('weight') else '-'
                })
            else:
                daily_df.append({
                    'Day': day_name,
                    'Date': day_date.strftime("%m/%d"),
                    'Treadmill': '-',
                    'Steps': '-', # Changed label
                    'Lunch Walk': '-',
                    'Total Exercise': '-',
                    'Strength': '-',
                    'Weight': '-'
                })
        
        df = pd.DataFrame(daily_df)
        st.dataframe(df, use_container_width=True)
        
    else:
        st.warning(f"No data logged for Week {selected_week} yet.")

def show_monthly_summary():
    st.header("📊 Monthly Summary")
    
    # Get available months
    if not st.session_state.tracker_data:
        st.warning("No data available yet.")
        return
    
    dates = [datetime.strptime(d, "%Y-%m-%d").date() for d in st.session_state.tracker_data.keys()]
    months = sorted(list(set((d.year, d.month) for d in dates)))
    
    if months:
        month_options = [f"{calendar.month_name[month]} {year}" for year, month in months]
        selected_month = st.selectbox("Select Month:", month_options)
        
        # Parse selected month
        year, month = months[month_options.index(selected_month)]
        
        # Get month data
        month_data = {}
        for date_str, data in st.session_state.tracker_data.items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            if date_obj.year == year and date_obj.month == month:
                month_data[date_str] = data
        
        if month_data:
            stats = get_summary_stats(month_data)
            
            st.subheader(f"📈 {calendar.month_name[month]} {year} Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Days Logged", stats['total_days'])
                st.metric("Total Exercise Time", f"{stats['total_exercise_time']:.0f} min")
            with col2:
                st.metric("Avg Treadmill/Day", f"{stats['avg_treadmill']:.1f} min")
                st.metric("Avg Steps/Day", f"{stats['avg_steps']:.0f}") # Changed label
            with col3:
                st.metric("Avg Lunch Walk/Day", f"{stats['avg_lunch_walks']:.1f} min")
                st.metric("Avg Exercise/Day", f"{stats['avg_exercise_time']:.1f} min")
            with col4:
                st.metric("Strength Sessions", stats['strength_sessions'])
                if stats['weight_change'] != 0:
                    st.metric("Weight Change", f"{stats['weight_change']:+.1f} kg")
            
            # Weekly breakdown within month
            st.subheader("📊 Weekly Trends")
            weekly_data = {}
            for date_str, data in month_data.items():
                week = data.get('week', get_week_number(date_str))
                if week not in weekly_data:
                    weekly_data[week] = []
                weekly_data[week].append(data)
            
            weekly_summary = []
            for week, week_entries in sorted(weekly_data.items()):
                week_stats = get_summary_stats({f"day_{i}": entry for i, entry in enumerate(week_entries)})
                weekly_summary.append({
                    'Week': week,
                    'Days Logged': week_stats['total_days'],
                    'Avg Treadmill': f"{week_stats['avg_treadmill']:.1f}",
                    'Avg Steps': f"{week_stats['avg_steps']:.0f}", # Changed label
                    'Avg Lunch Walk': f"{week_stats['avg_lunch_walks']:.1f}",
                    'Avg Total Exercise': f"{week_stats['avg_exercise_time']:.1f}",
                    'Strength Sessions': week_stats['strength_sessions']
                })
            
            if weekly_summary:
                df = pd.DataFrame(weekly_summary)
                st.dataframe(df, use_container_width=True)

def show_alltime_summary():
    st.header("📊 All-Time Summary")
    
    if not st.session_state.tracker_data:
        st.warning("No data available yet.")
        return
    
    stats = get_summary_stats(st.session_state.tracker_data)
    start_date, end_date = get_program_info()
    
    # Overall stats
    st.subheader("🎯 Overall Progress")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Days Logged", stats['total_days'])
        st.metric("Program Progress", f"{(stats['total_days']/210)*100:.1f}%")
    with col2:
        st.metric("Total Treadmill Time", f"{stats['total_treadmill']:.0f} min")
        st.metric("Total Steps", f"{stats['total_steps']:.0f}") # Changed label
    with col3:
        st.metric("Total Lunch Walk Time", f"{stats['total_lunch_walks']:.0f} min")
        st.metric("Total Exercise Time", f"{stats['total_exercise_time']:.0f} min")
    with col4:
        st.metric("Strength Sessions", stats['strength_sessions'])
        if stats['weight_change'] != 0:
            st.metric("Total Weight Change", f"{stats['weight_change']:+.1f} kg")
    
    # Trends
    if len(st.session_state.tracker_data) > 1:
        st.subheader("📈 Trends")
        
        # Prepare data for charts
        chart_data = []
        for date_str, data in sorted(st.session_state.tracker_data.items()):
            total_exercise = (data.get('treadmill_time', 0) + 
                              (data.get('steps', 0) / 100) + # Using steps in total exercise calculation
                              data.get('lunch_walk_time', 0))
            chart_data.append({
                'Date': date_str,
                'Treadmill': data.get('treadmill_time', 0),
                'Steps': data.get('steps', 0), # Changed variable
                'Lunch Walk': data.get('lunch_walk_time', 0),
                'Weight': data.get('weight', None),
                'Total Exercise': total_exercise
            })
        
        df = pd.DataFrame(chart_data)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Exercise Time Trend")
            st.line_chart(df[['Treadmill', 'Steps', 'Lunch Walk', 'Total Exercise']]) # Changed column name
        
        with col2:
            st.subheader("Weight Trend")
            weight_df = df[df['Weight'].notna()][['Weight']]
            if not weight_df.empty:
                st.line_chart(weight_df)
            else:
                st.info("Enter weight data to see trend")
    
    # Data export
    st.subheader("💾 Data Export")
    if st.button("📥 Export All Data"):
        json_data = json.dumps(st.session_state.tracker_data, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"lifestyle_tracker_complete_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()