
import streamlit as st
import pandas as pd
import plotly.express as px

from src.baseline import (
    load_data,
    validate_schedule,
    HORIZON,
    build_solar_profile,
    calculate_schedule_energy_metrics,
    calculate_schedule_comparison_metrics,
)
from src.optimizer import optimize_schedule

st.set_page_config(page_title="FlexFactory", page_icon="⚡", layout="wide")


def prepare_inputs(machine_rows, job_rows, price_rows):
    """Validate and convert values entered in the dashboard."""
    machines = pd.DataFrame(machine_rows)
    jobs = pd.DataFrame(job_rows)
    prices = pd.DataFrame(price_rows)

    if machines.empty or jobs.empty:
        raise ValueError("Add at least one machine and one production job.")

    if not {"machine_id", "machine_name"}.issubset(machines.columns):
        raise ValueError("Machine table is missing required columns.")

    if not {
        "job_id", "machine_id", "duration_hours", "power_kw",
        "release_hour", "deadline_hour"
    }.issubset(jobs.columns):
        raise ValueError("Job table is missing required columns.")

    if not {
        "start_hour", "end_hour", "price_per_kwh"
    }.issubset(prices.columns):
        raise ValueError("Electricity price table is missing required columns.")

    machines = machines.fillna("")
    jobs = jobs.copy()
    prices = prices.copy()

    machines["machine_id"] = machines["machine_id"].astype(str).str.strip()
    machines["machine_name"] = machines["machine_name"].astype(str).str.strip()
    jobs["job_id"] = jobs["job_id"].astype(str).str.strip()
    jobs["machine_id"] = jobs["machine_id"].astype(str).str.strip()

    if (machines["machine_id"] == "").any():
        raise ValueError("Every machine needs a machine ID.")
    if machines["machine_id"].duplicated().any():
        raise ValueError("Machine IDs must be unique.")
    if (jobs["job_id"] == "").any():
        raise ValueError("Every job needs a job ID.")
    if jobs["job_id"].duplicated().any():
        raise ValueError("Job IDs must be unique.")

    try:
        for column in ("duration_hours", "release_hour", "deadline_hour"):
            values = pd.to_numeric(jobs[column], errors="raise")
            if values.isna().any() or (values % 1 != 0).any():
                raise ValueError(f"{column} must contain whole numbers.")
            jobs[column] = values.astype(int)

        jobs["power_kw"] = pd.to_numeric(jobs["power_kw"], errors="raise")
        prices["start_hour"] = pd.to_numeric(
            prices["start_hour"], errors="raise"
        )
        prices["end_hour"] = pd.to_numeric(
            prices["end_hour"], errors="raise"
        )
        prices["price_per_kwh"] = pd.to_numeric(
            prices["price_per_kwh"], errors="raise"
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Check your numeric inputs: {exc}") from exc

    if jobs.isna().any().any() or prices.isna().any().any():
        raise ValueError("Input tables cannot contain empty numeric values.")
  

    machine_ids = set(machines["machine_id"])
    if not set(jobs["machine_id"]).issubset(machine_ids):
        raise ValueError("Every job must use a listed machine.")

    if (jobs["duration_hours"] <= 0).any():
        raise ValueError("Job durations must be positive.")
    if (jobs["power_kw"] < 0).any():
        raise ValueError("Power consumption cannot be negative.")
    if (jobs["release_hour"] < 0).any():
        raise ValueError("Release hours cannot be negative.")
    if (jobs["deadline_hour"] > HORIZON).any():
        raise ValueError(f"Deadlines cannot exceed hour {HORIZON}.")
    if (jobs["deadline_hour"] <= jobs["release_hour"]).any():
        raise ValueError("Each deadline must be later than its release hour.")
    if not set(jobs["machine_id"]).issubset(machine_ids):
        raise ValueError("Every job must use a machine listed in the machine table.")

        raise ValueError("Job durations must be positive.")
    if (jobs["power_kw"] < 0).any():
        raise ValueError("Power consumption cannot be negative.")
    if (jobs["release_hour"] < 0).any():
        raise ValueError("Release hours cannot be negative.")
    if (jobs["deadline_hour"] > HORIZON).any():
        raise ValueError(f"Deadlines cannot exceed hour {HORIZON}.")
    if (jobs["deadline_hour"] <= jobs["release_hour"]).any():
        raise ValueError("Each deadline must be later than its release hour.")

    for _, job in jobs.iterrows():
        if job["duration_hours"] > job["deadline_hour"] - job["release_hour"]:
            raise ValueError(f"{job['job_id']} cannot fit between its release and deadline.")

    if (prices["start_hour"] % 1 != 0).any() or (
        prices["end_hour"] % 1 != 0
    ).any():
        raise ValueError("Electricity price hours must be whole numbers.")

    prices["start_hour"] = prices["start_hour"].astype(int)
    prices["end_hour"] = prices["end_hour"].astype(int)

    if (prices["price_per_kwh"] % 1 != 0).any():
        raise ValueError(
        "Use whole-number electricity prices for now. "
        "Decimal tariff support needs an optimizer update."
    )


    if (prices["price_per_kwh"] % 1 != 0).any():
        raise ValueError(
            "Use whole-number electricity prices for now. "
            "Decimal tariff support needs an optimizer update."
        )

    if (jobs["power_kw"] * 2 % 1 != 0).any():
        raise ValueError(
            "Power values must use increments of 0.5 kW for now."
        )

    if (prices["price_per_kwh"] < 0).any():
        raise ValueError("Electricity prices cannot be negative.")

    if prices["start_hour"].duplicated().any():
        raise ValueError("Each electricity hour must appear only once.")

    price_map = {
        row["start_hour"]: row["end_hour"]
        for _, row in prices.iterrows()
    }

    for hour in range(HORIZON):
        if price_map.get(hour) != hour + 1:
            raise ValueError(
                f"Provide exactly one valid electricity price for hour {hour}."
            )

    return (
        machines.to_dict("records"),
        jobs.to_dict("records"),
        prices.to_dict("records"),
    )


def make_earliest_schedule(machines, jobs, prices):
    """Build a simple earliest-start baseline for comparison."""
    available = {m["machine_id"]: 0 for m in machines}
    schedule = []

    for job in sorted(
        jobs, key=lambda j: (j["release_hour"], j["deadline_hour"], j["job_id"])
    ):
        machine = job["machine_id"]
        start = max(job["release_hour"], available[machine])
        end = start + job["duration_hours"]

        if end > job["deadline_hour"] or end > HORIZON:
            return None

        schedule.append({
            "job_id": job["job_id"],
            "start_hour": start,
            "end_hour": end,
        })
        available[machine] = end

    if validate_schedule(machines, jobs, prices, schedule):
        return None

    return schedule


st.title("⚡ FlexFactory")
st.subheader("Interactive, energy-aware production scheduling")
st.caption(
    "Edit the example data or enter your own values, then optimize. "
    "The included dataset is simulated; results are not factory measurements."
)

try:
    default_machines, default_jobs, default_prices, _ = load_data()

    with st.form("factory_inputs"):
        st.header("1. Factory setup")
        st.write("Edit machine IDs and names. Add or remove rows if needed.")
        machines_df = st.data_editor(
            pd.DataFrame(default_machines),
            num_rows="dynamic",
            use_container_width=True,
            key="machine_editor",
        )

        machine_options = [
            str(value).strip()
            for value in machines_df.get("machine_id", pd.Series(dtype=str))
            if pd.notna(value) and str(value).strip()
        ]

        st.header("2. Production jobs")
        st.write("Change job requirements, deadlines, and machine assignments.")
        jobs_df = st.data_editor(
            pd.DataFrame(default_jobs),
            num_rows="dynamic",
            use_container_width=True,
            key="job_editor",
            column_config={
                "machine_id": st.column_config.SelectboxColumn(
                    "Machine",
                    options=machine_options,
                    required=True,
                ),
                "duration_hours": st.column_config.NumberColumn(
                    "Duration (hours)", min_value=1, step=1
                ),
                "power_kw": st.column_config.NumberColumn(
                    "Power (kW)", min_value=0.0, step=0.5
                ),
                "release_hour": st.column_config.NumberColumn(
                    "Release hour", min_value=0, max_value=HORIZON - 1, step=1
                ),
                "deadline_hour": st.column_config.NumberColumn(
                    "Deadline hour", min_value=1, max_value=HORIZON, step=1
                ),
            },
        )

        st.header("3. Hourly electricity prices")
        st.write("Change the price for each hour. The planning horizon is fixed at 12 hours.")
        prices_df = st.data_editor(
            pd.DataFrame(default_prices),
            disabled=["start_hour", "end_hour"],
            use_container_width=True,
            hide_index=True,
            key="price_editor",
            column_config={
                "price_per_kwh": st.column_config.NumberColumn(
                    "Price (₹/kWh)", min_value=0.0, step=1.0
                )
            },
        )

        submitted = st.form_submit_button(
            "⚡ Optimize Schedule", type="primary", use_container_width=True
        )

    if submitted:
        try:
            machines, jobs, prices = prepare_inputs(
                machines_df.to_dict("records"),
                jobs_df.to_dict("records"),
                prices_df.to_dict("records"),
            )

            optimized, status = optimize_schedule(machines, jobs, prices)
            errors = validate_schedule(machines, jobs, prices, optimized)

            if errors:
                raise ValueError("Optimizer schedule validation failed: " + "; ".join(errors))

            baseline = make_earliest_schedule(machines, jobs, prices)

            result = {
                "machines": machines,
                "jobs": jobs,
                "prices": prices,
                "optimized": optimized,
                "status": status,
                "baseline": baseline,
            }

            st.session_state["flexfactory_result"] = result

        except Exception as exc:
            st.session_state["flexfactory_result"] = {"error": str(exc)}

    result = st.session_state.get("flexfactory_result")

    if result:
        if "error" in result:
            st.error(f"Could not optimize these inputs: {result['error']}")
        else:
            optimized = result["optimized"]
            jobs = result["jobs"]
            prices = result["prices"]

            st.success(f"Optimization completed — solver status: {result['status']}")

            solar_profile = build_solar_profile()
            solar_df = pd.DataFrame(solar_profile)
            solar_df = solar_df.rename(columns={"solar_available_kwh": "solar_available_kwh"})

            st.header("4. Simulated cost and solar use")
            st.caption(
                "Tariffs and solar availability use the supplied project CSVs unless edited above. "
                "Costs and savings are simulated estimates, not measured factory results."
            )

            factor = st.slider(
                "Illustrative emissions factor (kg CO₂/kWh)",
                min_value=0.1,
                max_value=1.5,
                value=0.45,
                step=0.05,
            )

            solar_chart = px.line(
                solar_df,
                x="hour",
                y="solar_available_kwh",
                markers=True,
                title="Simulated hourly solar availability profile",
                labels={"hour": "Hour", "solar_available_kwh": "Solar available (kWh)"},
            )
            st.plotly_chart(solar_chart, use_container_width=True)

            if result["baseline"] is not None:
                comparison_metrics = calculate_schedule_comparison_metrics(
                    result["baseline"],
                    optimized,
                    jobs,
                    prices,
                    solar_profile,
                    emissions_factor=factor,
                )
                baseline_metrics = comparison_metrics["baseline"]
                optimized_metrics = comparison_metrics["optimized"]

                comparison_table = pd.DataFrame([
                    {
                        "Scenario": "Earliest-start baseline",
                        "Gross electricity cost (₹)": baseline_metrics["gross_cost_rupees"],
                        "Grid electricity cost (₹)": baseline_metrics["grid_cost_rupees"],
                        "Grid energy (kWh)": baseline_metrics["grid_energy_kwh"],
                        "Solar energy used (kWh)": baseline_metrics["solar_used_kwh"],
                    },
                    {
                        "Scenario": "Optimized",
                        "Gross electricity cost (₹)": optimized_metrics["gross_cost_rupees"],
                        "Grid electricity cost (₹)": optimized_metrics["grid_cost_rupees"],
                        "Grid energy (kWh)": optimized_metrics["grid_energy_kwh"],
                        "Solar energy used (kWh)": optimized_metrics["solar_used_kwh"],
                    },
                ])
                st.dataframe(comparison_table, use_container_width=True, hide_index=True)

                reduction_percent = comparison_metrics["grid_cost_reduction_percent"]
                reduction_delta = (
                    f"{reduction_percent:.2f}% of baseline grid cost"
                    if reduction_percent is not None
                    else "Baseline grid cost is zero"
                )
                st.metric(
                    "Simulated grid-cost reduction",
                    f"₹{comparison_metrics['grid_cost_reduction_rupees']:.2f}",
                    delta=reduction_delta,
                )
                st.caption(
                    "Reduction is baseline grid electricity cost minus optimized grid electricity cost. "
                    "A negative value means the optimized schedule costs more from the grid."
                )

                a, b = st.columns(2)
                a.metric("Baseline estimated CO₂", f"{baseline_metrics['estimated_emissions_kg']:.2f} kg")
                b.metric("Optimized estimated CO₂", f"{optimized_metrics['estimated_emissions_kg']:.2f} kg")

                comparison = pd.DataFrame({
                    "Scenario": ["Earliest-start", "Optimized"],
                    "Grid energy (kWh)": [baseline_metrics["grid_energy_kwh"], optimized_metrics["grid_energy_kwh"]],
                    "Estimated CO₂ (kg)": [baseline_metrics["estimated_emissions_kg"], optimized_metrics["estimated_emissions_kg"]],
                })
                fig_emissions = px.bar(
                    comparison,
                    x="Scenario",
                    y=["Grid energy (kWh)", "Estimated CO₂ (kg)"],
                    title="Grid-energy and emissions comparison",
                )
                st.plotly_chart(fig_emissions, use_container_width=True)

                st.caption(
                    f"Solar share: baseline {baseline_metrics['solar_share'] * 100:.1f}% vs optimized {optimized_metrics['solar_share'] * 100:.1f}%."
                )
            else:
                optimized_metrics = calculate_schedule_energy_metrics(
                    optimized, jobs, prices, solar_profile, emissions_factor=factor
                )
                st.dataframe(pd.DataFrame([{
                    "Scenario": "Optimized",
                    "Gross electricity cost (₹)": optimized_metrics["gross_cost_rupees"],
                    "Grid electricity cost (₹)": optimized_metrics["grid_cost_rupees"],
                    "Grid energy (kWh)": optimized_metrics["grid_energy_kwh"],
                    "Solar energy used (kWh)": optimized_metrics["solar_used_kwh"],
                }]), use_container_width=True, hide_index=True)
                st.metric("Estimated grid emissions", f"{optimized_metrics['estimated_emissions_kg']:.2f} kg CO₂")
                st.info(
                    "A valid earliest-start baseline could not be generated for these inputs. "
                    "Cost reduction is not shown."
                )
                st.caption(f"Solar share: {optimized_metrics['solar_share'] * 100:.1f}%.")

            st.header("5. Optimized production schedule")
            optimized_df = pd.DataFrame(optimized).merge(
                pd.DataFrame(result["jobs"])[["job_id", "machine_id"]],
                on="job_id",
                how="left",
            )
            st.dataframe(
                optimized_df.sort_values(["start_hour", "machine_id"]),
                use_container_width=True,
                hide_index=True,
            )

            fig = px.bar(
                optimized_df,
                x="start_hour",
                y="job_id",
                color="machine_id",
                orientation="h",
                title="Optimized job start hours by machine",
                labels={"start_hour": "Start hour", "job_id": "Production job"},
            )
            st.plotly_chart(fig, use_container_width=True)

            
            
            
            st.header("6. Production timeline")

            import plotly.express as px

            gantt_df = optimized_df.copy()
            gantt_df["Start"] = pd.to_numeric(
                gantt_df["start_hour"], errors="coerce"
            )
            gantt_df["Finish"] = pd.to_numeric(
                gantt_df["end_hour"], errors="coerce"
            )

            fig_gantt = px.bar(
                gantt_df,
                x="Finish",
                y="machine_id",
                base="Start",
                color="job_id",
                orientation="h",
                hover_data=["start_hour", "end_hour"],
                title="Optimized Production Timeline",
            )

            fig_gantt.update_layout(
                height=450,
                xaxis_title="Hour",
                yaxis_title="Machine",
                xaxis=dict(range=[0, 12], dtick=1),
            )

            st.plotly_chart(
                fig_gantt,
                use_container_width=True,
                key="production_gantt",
            )

            st.header("7. Download results")
            st.download_button(
                "Download optimized schedule (CSV)",
                data=optimized_df.to_csv(index=False).encode("utf-8"),
                file_name="optimized_schedule.csv",
                mime="text/csv",
            )

            st.caption(
                "Results depend on the values entered and the simplified model. "
                "They are not a guarantee of real-world savings or emissions reductions."
            )

except FileNotFoundError as exc:
    st.error(f"Required project file not found: {exc}")
except Exception as exc:
    st.error(f"FlexFactory could not load: {exc}")
