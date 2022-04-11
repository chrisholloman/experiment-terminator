import altair as alt
from experiment_terminator import ExperimentTerminator
import numpy as np
import pandas as pd
import streamlit as st


def analyze_experiment():
    """
    Upon clicking the button, run the experiment analyzer and display all of the output. This even
    displays a histogram and some Arnold images.
    """

    exp_output = et.analyze_experiment(planned_trials_a,
                                       planned_trials_b,
                                       completed_trials_a,
                                       completed_trials_b,
                                       successes_a,
                                       successes_b)

    # Only display the parameter summary information after the analysis has concluded.
    input_summary.markdown(input_display)
        
    # Display the summary statistics about the posterior distribution and posterior predictive
    # distribution
    output_col1.metric("Observed Conversion Rate in Control Group", value=np.round(exp_output[0], 4))
    output_col2.metric("Observed Conversion Rate in Test Group", value=np.round(exp_output[1], 4))
    output_col3.metric("Estimated Lift (Posterior Mean)", value=str(np.round(100 * exp_output[2], 2)) + "%")
    output_col4.metric("Probability Test Rate > Control Rate", value=np.round(exp_output[3], 4))
    output_col5.metric("Probability of Significance at Experiment End", value=np.round(exp_output[4], 4))

    # Apply logic determining what conclusion is reached.
    if exp_output[4] < 0.01 or exp_output[4] > .99:  # We know the future of the experiment - conclude.
        outstring = "## Experiment can be terminated. "
        if exp_output[4] < .01:  # The future is that there is almost no way we'll see significance
            outstring += "No difference between experiment and control will be found."
        else:  # The future is that we almost certainly will see significance
            if exp_output[3] > .5:
                outstring += "Test is superior to control."
            else:
                outstring += "Control is superior to test."
        conclusion_container.markdown(outstring)

        # Add an Arnold image to drive home the point.
        graph_col1.image('images/terminator_okay.gif', use_column_width=True)
    else:
        # We don't know the future of the experiment. Continue
        conclusion_container.markdown("## Experiment should not be terminated.")
        # Add an Arnold image to drive home the point.
        graph_col1.image('images/thou_shalt_not_terminate.jpeg', use_column_width=True)

    # Create the histogram showing the posterior distribution of lifts.
    chart_data = pd.DataFrame({'lift': exp_output[5]})
    chart = alt.Chart(chart_data).mark_bar().encode(
        alt.X("lift", bin=alt.Bin(maxbins=30)),
        y="count()"
    ).properties(title="Histogram of Posterior Distribution of Lift")
    graph_col2.altair_chart(chart, use_container_width=True)

et = ExperimentTerminator()

# Set overall page configuration variables
st.set_page_config(layout="wide")
st.title('Experiment Terminator')

# Create the container where users can input information about their experiment.
main_container = st.container()

# Create input boxes in two columns, one for Control and one for Test. For each one, 
# make input boxes for planned number of trials, completed trials, and successes.
col1, col2 = main_container.columns(2)
col1.header("Control")
planned_trials_a = col1.number_input("Planned Number of Trials", min_value=100, key='planned_trials_a', value=500)
completed_trials_a = col1.number_input("Completed Trials", min_value=100, max_value=planned_trials_a, key='completed_trials_a', value=300)
successes_a = col1.number_input("Successes", min_value=0, key='successes_a', value=25)

col2.header("Test")
planned_trials_b = col2.number_input("Planned Number of Trials", min_value=100, key='planned_trials_b', value=500)
completed_trials_b = col2.number_input("Completed Trials", min_value=100, max_value=planned_trials_b, key='completed_trials_b', value=300)
successes_b = col2.number_input("Successes", min_value=0, key='successes_b', value=35)

# Add a button to click to make the analysis run.
analyze = st.button("Analyze Experiment for Termination", on_click=analyze_experiment)

# Add a container to holds summary information on the parameters used to run the analysis. This gets
# displayed back to the user so they know what information the code is using.
input_summary = st.container()
input_display = "Analysis run with the following parameters: Control Group ("
input_display += str(planned_trials_a) + " planned trials, "
input_display += str(completed_trials_a) + " completed trials, "
input_display += str(successes_a) + " successes), Test Group ("
input_display += str(planned_trials_b) + " planned trials, "
input_display += str(completed_trials_b) + " completed trials, "
input_display += str(successes_b) + " successes)"
input_summary.markdown("")

# Add a container to hold summary statistics about the posterior distribution and posterior
# predictive distribution.
result_container = st.container()
output_col1, output_col2, output_col3, output_col4, output_col5 = result_container.columns(5)

# Add a container with a text statement about the conclusions reached.
conclusion_container = st.container()
conclusion_container.markdown("")

# Add a container to hold graphiics. This will hold an Arnold graphic on the left and a histogram on the right.
graph_container = st.container()
graph_col1, graph_col2 = graph_container.columns(2)
graph_col1.markdown("")
graph_col2.markdown("")