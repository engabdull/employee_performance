frappe.pages['employee-performance'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __('Employee Performance'),
        single_column: true
    });

    render_layout(page);
    init_dashboard(page);
};

function render_layout(page) {
    let $parent = $(page.body);
    $parent.empty();

    let greeting = get_dynamic_greeting();

    let html = `
		<div class="epd-dashboard">
			<!-- Top Header -->
			<div class="epd-header">
				<div class="epd-greeting">
					<h1 id="epd-greeting-text">${greeting}</h1>
					<p>${__('Here is a performance overview for Last Month.')}</p>
				</div>
				<div class="epd-filter" id="employee-selector-container"></div>
			</div>

			<!-- 4-Card KPI Grid -->
			<div class="epd-kpi-grid">
				<div class="kpi-card bg-teal">
					<div class="card-value" data-field="total_leads">0</div>
					<div class="card-label">${__("Total Leads")}</div>
					<i class="fa fa-user-plus card-icon" style="opacity: 0.2;"></i>
				</div>
				<div class="kpi-card bg-orange">
					<div class="card-value" data-field="total_opportunities">0</div>
					<div class="card-label">${__("Opportunities")}</div>
					<i class="fa fa-lightbulb card-icon" style="opacity: 0.2;"></i>
				</div>
				<div class="kpi-card bg-blue">
					<div class="card-value" data-field="active_customers">0</div>
					<div class="card-label">${__("Customers")}</div>
					<i class="fa fa-user-check card-icon" style="opacity: 0.2;"></i>
				</div>
				<div class="kpi-card bg-purple">
					<div class="card-value" data-field="conversion_rate">0%</div>
					<div class="card-label">${__("Conversion Rate")}</div>
					<i class="fa fa-percentage card-icon" style="opacity: 0.2;"></i>
				</div>
			</div>

			<!-- Main Content: Horizontal Split -->
			<div class="epd-main-row">
				<!-- Left: Reports & Trend -->
				<div class="epd-content-section">
					<div class="section-title">
						${__("Monthly Activity Distribution")}
						<span>${__("Events & Categories")}</span>
					</div>
					<div id="main-distribution-chart" style="height: 350px; min-height: 350px;"></div>
                    
                    <div style="margin-top: 40px;">
                        <div class="section-title">${__("Leads Pulse")}</div>
                        <div id="leads-pulse-chart" style="height: 200px; min-height: 200px;"></div>
                    </div>
				</div>

				<!-- Right: Attendance & Log -->
				<div class="epd-content-section">
					<div class="section-title">${__("Attendance Overview")}</div>
					<div id="attendance-donut-chart" style="height: 280px; min-height: 280px;"></div>
					
					<div class="epd-table-container" style="margin-top: 20px;">
						<div class="section-title">${__("Recent Activity Log")}</div>
                        <div class="compact-timeline" id="checkin-timeline" style="min-height: 100px;"></div>
					</div>
				</div>
			</div>

            <!-- Bottom Row: Multi-Column Performance Table -->
            <div class="epd-table-container" style="margin-top: 20px;">
                <div class="epd-content-section">
                    <div class="section-title">${__("Comprehensive Performance Metrics")}</div>
                    <table class="epd-table">
                        <thead>
                            <tr>
                                <th>${__("Indicator")}</th>
                                <th>${__("Value")}</th>
                                <th>${__("Description")}</th>
                            </tr>
                        </thead>
                        <tbody id="performance-body">
                            <tr>
                                <td><div class="emp-name">${__("Total Attendance")}</div></td>
                                <td data-field="attendance_total">0</td>
                                <td><div class="emp-meta">${__("Total present days in the last month.")}</div></td>
                            </tr>
                            <tr>
                                <td><div class="emp-name">${__("Daily Report Count")}</div></td>
                                <td data-field="daily_report">0</td>
                                <td><div class="emp-meta">${__("Total recorded logs for the last month.")}</div></td>
                            </tr>
                            <tr>
                                <td><div class="emp-name">${__("Appointments")}</div></td>
                                <td data-field="appointments">0</td>
                                <td><div class="emp-meta">${__("Scheduled sessions processed.")}</div></td>
                            </tr>
                            <tr>
                                <td><div class="emp-name">${__("Total Task")}</div></td>
                                <td data-field="total_task">0</td>
                                <td><div class="emp-meta">${__("Total tasks assigned in the last month.")}</div></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
		</div>
	`;

    $(html).appendTo($parent);
}

function get_dynamic_greeting() {
    let hour = new Date().getHours();
    if (hour < 12) return __('Good Morning');
    if (hour < 17) return __('Good Afternoon');
    return __('Good Evening');
}

function init_dashboard(page) {
    let selector = frappe.ui.form.make_control({
        parent: $('#employee-selector-container'),
        df: {
            label: '',
            fieldtype: 'Link',
            fieldname: 'employee',
            options: 'Employee',
            placeholder: __('Choose employee'),
            change: function () {
                refresh_dashboard(selector.get_value());
            }
        },
        render_input: true
    });

    frappe.db.get_value('Employee', { user_id: frappe.session.user }, 'name').then(r => {
        if (r && r.message && r.message.name) {
            selector.set_value(r.message.name);
            refresh_dashboard(r.message.name);
        }
    });

    page.employee_selector = selector;
}

function refresh_dashboard(employee) {
    if (!employee) return;
    frappe.call({
        method: 'employee_performance.employee_performance.page.employee_performance.employee_performance.get_employee_dashboard',
        args: { employee: employee },
        callback: function (r) {
            if (r.message) {
                update_ui(r.message);
            }
        }
    });
}

function update_ui(data) {
    if (!data) {
        console.error("EPD: No data received in update_ui");
        return;
    }
    console.log("EPD: Update UI with data:", data);

    // KPI cards
    $('[data-field="total_leads"]').text(data.crm.total_leads || 0);
    $('[data-field="total_opportunities"]').text(data.crm.total_opportunities || 0);
    $('[data-field="active_customers"]').text(data.crm.active_customers || 0);
    $('[data-field="conversion_rate"]').text((data.crm.conversion_rate || 0) + '%');

    // Table metrics
    $('[data-field="attendance_total"]').text(data.hr.present_days || 0);
    $('[data-field="daily_report"]').text(data.daily_report || 0);
    $('[data-field="appointments"]').text(data.appointments ? data.appointments.total || 0 : 0);
    $('[data-field="total_task"]').text(data.total_task || 0);

    // FIX: Replace fragile setTimeout with a retry-based readiness check.
    // This prevents silent failures when frappe.Chart hasn't loaded yet.
    render_charts_when_ready(data);

    // Timeline doesn't depend on frappe.Chart — render immediately
    try {
        render_activity_timeline(data.hr.recent_checkins);
    } catch (e) {
        console.error("EPD: Error in timeline", e);
    }
}

/**
 * FIX: Retry loop instead of a one-shot setTimeout.
 * Retries every 300ms up to `maxRetries` times before giving up.
 */
function render_charts_when_ready(data, retries) {
    // Default to 10 retries (= 3 seconds total wait)
    if (retries === undefined) retries = 10;

    if (window.frappe && frappe.Chart) {
        console.log("EPD: frappe.Chart ready — rendering charts");
        try { render_main_dist(data.events_chart); } catch (e) { console.error("EPD: main distribution chart error", e); }
        try { render_leads_pulse(data.leads_pulse); } catch (e) { console.error("EPD: leads pulse chart error", e); }
        try { render_attendance_donut(data.attendance_chart); } catch (e) { console.error("EPD: attendance donut error", e); }
    } else if (retries > 0) {
        console.warn(`EPD: frappe.Chart not ready yet — retrying (${retries} left)`);
        setTimeout(() => render_charts_when_ready(data, retries - 1), 300);
    } else {
        console.error("EPD: frappe.Chart never became available after max retries");
    }
}

function render_main_dist(data) {
    let container = "#main-distribution-chart";
    if (!$(container).length) return;
    $(container).empty();

    if (!data || !data.labels || data.labels.length === 0) {
        $(container).html(`<div class="text-muted text-center" style="padding: 60px 20px;">${__('No activity data for last month')}</div>`);
        return;
    }

    // FIX: Guard against all-zero values to avoid rendering an empty chart frame
    let total = (data.values || []).reduce((a, b) => a + b, 0);
    if (total === 0) {
        $(container).html(`<div class="text-muted text-center" style="padding: 60px 20px;">${__('No activity data for last month')}</div>`);
        return;
    }

    new frappe.Chart(container, {
        data: {
            labels: data.labels,
            datasets: [{ name: __("Activity"), values: data.values }]
        },
        type: 'bar',
        height: 350,
        colors: ['#3b82f6'],
        barOptions: { spaceRatio: 0.2 },
        axisOptions: { xIsSeries: 1 }
    });
}

function render_leads_pulse(data) {
    let container = "#leads-pulse-chart";
    if (!$(container).length) return;
    $(container).empty();

    if (!data || !data.labels || data.labels.length === 0) {
        $(container).html(`<div class="text-muted text-center" style="padding: 40px 20px;">${__('No leads data for last month')}</div>`);
        return;
    }

    // FIX: Guard against all-zero before rendering
    let total = (data.values || []).reduce((a, b) => a + b, 0);
    if (total === 0) {
        $(container).html(`<div class="text-muted text-center" style="padding: 40px 20px;">${__('No leads data for last month')}</div>`);
        return;
    }

    new frappe.Chart(container, {
        data: {
            labels: data.labels,
            datasets: [{ name: __("Leads"), values: data.values }]
        },
        type: 'line',
        height: 200,
        colors: ['#a855f7'],
        lineOptions: { regionFill: 1, hideDots: 1 }
    });
}

function render_attendance_donut(data) {
    let container = "#attendance-donut-chart";
    if (!$(container).length) return;
    $(container).empty();

    if (!data || !data.labels || data.labels.length === 0) {
        $(container).html(`<div class="text-muted text-center" style="padding: 60px 20px;">${__('No attendance data for last month')}</div>`);
        return;
    }

    // FIX: Guard against all-zero — frappe.Chart donut crashes on empty data
    let total = (data.values || []).reduce((a, b) => a + b, 0);
    if (total === 0) {
        $(container).html(`<div class="text-muted text-center" style="padding: 60px 20px;">${__('No attendance data for last month')}</div>`);
        return;
    }

    new frappe.Chart(container, {
        data: {
            labels: data.labels,
            datasets: [{ values: data.values }]
        },
        type: 'donut',
        height: 280,
        colors: ['#22c55e', '#ef4444', '#f59e0b'],
        donutOptions: { strokeWidth: 40 }
    });
}

function render_activity_timeline(reports) {
    let $container = $('#checkin-timeline');
    if (!$container.length) return;
    $container.empty();

    if (!reports || reports.length === 0) {
        $container.append(`<div class="text-muted text-center" style="padding: 20px;">${__('No reports found')}</div>`);
        return;
    }

    reports.slice(0, 10).forEach(log => {
        let date = frappe.datetime.global_date_format(log.time);
        $container.append(`
			<div class="timeline-row">
				<div class="emp-name" style="max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                    ${log.device_id || __('Daily Report')}
                </div>
				<div class="timeline-log-type log-in">${date}</div>
			</div>
		`);
    });
}