import React, { useState, useEffect } from 'react';
import { useSpring, animated } from 'react-spring';

import "./Progressbar.css";

import { getStatus } from "../../Upload/function/getStatus";

const ProgressBar = (props) => {

    // const [progress, updateProgress] = useState(10);

    const [progress, animate] = useSpring(() => ({
        config: { duration: 1800 },
        width: 0 + "%",
    }));

    const [textOp, fade] = useSpring(() => ({
        opacity: 0,
    }));

    const [progressMessage, updateMessage] = useState("Application not yet started");

    const update = (newMessage, percentage) => {
        fade({ opacity: 0, delay: 1000 });
        fade({ opacity: 1, delay: 500 });
        updateMessage(newMessage);
        animate({ width: (percentage <= 100 ? percentage : 100) + "%", delay: 500 });

    };

    useEffect(() => {
        const task_url = "http://localhost:5005/task";
        getStatus(task_url, props.uuid);
    }, []);

    return (
        <>
            <div style={{ width: 900, height: 50, background: "#FFF", borderRadius: 14, mariginLeft: 150, padding: 4, ...props.style, marginTop: 100 }}>
                <animated.div className="stage" style={{ borderRadius: 17, height: "99%", ...progress }}>
                </animated.div>
            </div>

            <animated.p style={{ ...textOp, color: "#FFF", fontWeight: "bold" }}>{progressMessage}</animated.p>
        </>
    );
};

export default ProgressBar;
