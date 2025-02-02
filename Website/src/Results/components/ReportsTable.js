import React from "react";

import "./ReportsTable.css";
import Modal from "react-bootstrap/Modal";


export default function ReportsTable({ image, issues, app }) {
    const [modalShow, setModalShow] = React.useState(false);

    return (
        <>
          <h2 style={{ color: "white" }}>{app}</h2>
          <p style={{ color: "white" }}>
            click each image to retrieve more infomation
          </p>
          <div id="report">
            {/* <img id='report_img' src={require("../content/bug_screenshot.PNG")} alt="issue" /> */}
            <div className="imageContainer">
              <img
                id="report_img"
                src={"../content/xbot/a2dp.Vol.AppChooser.png"}
        //src="../content/bug_screenshot.PNG"
        //src={image}
        //src={require({image})}
                alt={""}
              />
              <img
                className="imageOverlay"
                src={"../content/expand_icon.png"}
                onClick={() => setModalShow(true)}
                alt={""}
              />
            </div>

            <img
              id="report_img"
              src={"../content/xbot/a2dp.Vol.CustomIntentMaker.png"}
              onClick={() => setModalShow(true)}
              alt={""}
            />

            <img
              id="report_img"
              src={"../content/xbot/a2dp.Vol.main.png"}
              onClick={() => setModalShow(true)}
              alt={""}
            />

            <MyVerticallyCenteredModal
              show={modalShow}
              onClick={() => setModalShow(false)}
              onHide={() => setModalShow(false)}
            />

            {/* <p>
               {
               issues.map((issue) => (
               <li style={{ float: "right", width: "80%", margin: "12px 0px 0px 10px" }}>{issue}</li>
               ))
               }
               </p> */}
          </div>

          <h2 style={{ color: "white" }}>OwlEye</h2>
          <p> </p>
          <div id="report">
            <img
              id="report_img"
              src={"../content/owleye/a2dp.Vol.AppChooser.jpg"}
              onClick={() => setModalShow(true)}
              alt={""}
            />

            <img
              id="report_img"
              src={"../content/owleye/a2dp.Vol.CustomIntentMaker.jpg"}
              onClick={() => setModalShow(true)}
              alt={""}
            />

            <img
              id="report_img"
              src={"../content/owleye/a2dp.Vol.main.jpg"}
              onClick={() => setModalShow(true)}
              alt={""}
            />


            <MyVerticallyCenteredModal
              show={modalShow}
              onClick={() => setModalShow(false)}
              onHide={() => setModalShow(false)}
            />
          </div>
        </>
    );
}

function MyVerticallyCenteredModal(props) {
    return (
        <Modal
          {...props}
          size="lg"
          aria-labelledby="contained-modal-title-vcenter"
          centered
        >
          <Modal.Header closeButton>
            <Modal.Title id="contained-modal-title-vcenter">
              Detected issues
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>
              The following is a list of opportunities to improve the accessibility
              of A2DP Volume. Each item corresponds to an outlined area on the
              attached screenshot.
            </p>
            <li>
              Item label a2dp.Vol:id/m_et_search This item may not have a label
              readable by screen readers.
            </li>
            <li>
              Text contrast a2dp.Vol:id/pi_tv_name The item's text contrast ratio is
              1.99. This ratio is based on an estimated foreground color of #B4B4B4
              and an estimated background color of #FAFAFA. Consider increasing this
              item's text contrast ratio to 3.00 or greater.
            </li>
            <li>
              Text contrast a2dp.Vol:id/pi_tv_name The item's text contrast ratio is
              1.04. This ratio is based on an estimated foreground color of #FFFFFF
              and an estimated background color of #FAFAFA. Consider increasing this
              item's text contrast ratio to 3.00 or greater.
            </li>
            <li>
              Text contrast a2dp.Vol:id/pi_tv_name The item's text contrast ratio is
              1.04. This ratio is based on an estimated foreground color of #FFFFFF
              and an estimated background color of #FAFAFA. Consider increasing this
              item's text contrast ratio to 3.00 or greater.
            </li>
          </Modal.Body>
        </Modal>
    );
}
