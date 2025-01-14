import React, { useState, useEffect } from "react";
import { Container } from "react-bootstrap";
import { Link, useLocation } from "react-router-dom";

import "./Upload.css";
import "../index.css";
import "../components/button.css";

import UploadBox from "./components/UploadBox";

const Upload = () => {
    const [currentAppStatus, updateCurrentAppStatus] = useState("READY");

    const locations = useLocation();

    const tempState = locations.state?.objectState;

    const [objectState, setObjectState] = useState(tempState);

    useEffect(() => {

        var myNavbar = document.getElementById("myNavbar");
        myNavbar.classList.remove("sticky");

        window.scrollTo(0, 0);

    }, []);


    if (typeof objectState === "undefined") {
        setObjectState({
            uuid: null,
            apk: null,
            algorithms: [
                {
                    uuid: "gifdroid",
                    algorithmName: "GifDroid",
                    requiresAdditionalInput: true,
                    additionalInputDescription:
                    "Requires a screen recorded video of the app",
                    additionalInputFileTypes: {
                        "image/gif": [".gif"],
                    },
                    additionalFiles: [],
                    description:
                    "GifDroid generates a UTG graph",
                    selected: false,
                },
                {
                    uuid: "venus",
                    algorithmName: "Venus",
                    requiresAdditionalInput: false,
                    additionalInputDescription: "Requires a .dl file",
                    additionalInputFileTypes: {},
                    additionalFiles: [],
                    description:
                    "Venus explores accessibility issues in an application",
                    selected: false,
                },
                {
                    uuid: "owleye",
                    algorithmName: "OwlEye",
                    requiresAdditionalInput: false,
                    additionalInputDescription: "Does not require any additional uploads",
                    additionalInputFileTypes: {},
                    additionalFiles: [],
                    description:
                    "Owl eye can automatically detect and localize UI display issues in the screenshots of the application under test",
                    selected: false,
                },
                {
                    uuid: "xbot",
                    algorithmName: "xBot",
                    requiresAdditionalInput: false,
                    additionalInputDescription: "Does not require any additional uploads",
                    additionalInputFileTypes: {},
                    additionalFiles: [],
                    description:
                    "xBot specializes in accessibility testing of Android apps",
                    selected: false,
                },
                {
                    uuid: "tappable",
                    algorithmName: "Tappable",
                    requiresAdditionalInput: false,
                    additionalInputDescription: "Does not require any additional uploads",
                    additionalInputFileTypes: {},
                    additionalFiles: [],
                    description:
                    "Tappable is able to identify clickable objects which may have poor usability and be perceived as unclickable",
                    selected: false,
                },
            ],
        });
    }

    const [buttonState, setButtonState] = useState(true);

    const uploadState = (state) => {
        objectState.apk = state.selectedFile;
        setObjectState(objectState);
        setButtonState(state.buttonState);
    };

    return (
        <Container className="container-nav">
          <div className="root">
            <p className="text-header text-centre">UPLOAD YOUR APK</p>
            <p className="text text-centre">
              To begin the process, upload an APK file. For an example of the
              process and results see the About page.
            </p>

            <div className="vspacing-40"> </div>

            <div className="upload-div-group-white">
              <UploadBox
                currentAppStatus={currentAppStatus}
                updateCurrentAppStatus={updateCurrentAppStatus}
                acceptedFileTypes={{ "application/octet-stream": [".apk"] }}
                method={uploadState}
              />
            </div>

            <Link
              to={"./selectalgorithm"}
              style={buttonState ? { pointerEvents: "none" } : {}}
              state={{ objectState: objectState }}
            >
              <button className="cust_button next-button" disabled={buttonState}>
                <h3>Next</h3>
              </button>
            </Link>
          </div>
        </Container>
    );
};

export default Upload;
